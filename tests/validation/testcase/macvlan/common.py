import json
import time
import random
import netaddr
import ipaddress

from ..entfunc import * # NOQA
from ..common_v1 import * # NOQA


factory = {'client': None,
           'v3_admin_client': None,
           'cluster': None,
           'pandaria_catalog': None,
           'project': None,
           'ns': None,
           'subnet': None,
           'worker_nodes': None}
wl_selector = "workload.user.cattle.io/workloadselector"
eth0_network = '[{\"name\":\"static-macvlan-cni-attach\",\"interface\":\"eth0\"}]'
eth0_anno_key = "v1.multus-cni.io/default-network"
eth1_network = '[{\"name\":\"static-macvlan-cni-attach\",\"interface\":\"eth1\"}]'
eth1_anno_key = "k8s.v1.cni.cncf.io/networks"

DEFAULT_MASTER = os.environ.get('RANCHER_TEST_SUBNET_MASTER', "ens4")
BUSYBOX_IMAGE = os.environ.get('RANCHER_TEST_BUSYBOX_IMAGE', "busybox:glibc")
NGINX_IMAGE = os.environ.get('RANCHER_TEST_NGINX_IMAGE', "nginx")

MACVLAN_SERVICE_SUFFIX="-macvlan"
REQUEST_TIMEOUT=5


def get_common_workload_pods(client, wl):
    label_key = 'workload.user.cattle.io/workloadselector'
    ns_name = wl["metadata"]["namespace"]
    wl_name = wl["metadata"]["name"]
    wl_type = wl["type"]
    label_value = f'{wl_type}-{ns_name}-{wl_name}'
    pods = client.list_pod(labelSelector=f'{label_key}={label_value}').data

    return pods

def get_macvlan_pod_ip(pod, nic="eth1", ipv6=False):
    base = "ip -4 addr show dev "
    if ipv6:
        base = "ip -6 addr show dev "
    cmd = base + nic + "| grep 'inet' |awk '{print $2}'| cut -d '/' -f1"
    result = get_kubectl_exec_output(pod["metadata"]["name"],
                                     pod["metadata"]["namespace"],
                                     cmd)
    return result.split("\n")[0]


def get_macvlan_pod_mac(pod):
    cmd = "ip addr show dev eth1 |grep 'ether' | awk '{print $2}'"
    result = get_kubectl_exec_output(pod["metadata"]["name"],
                                     pod["metadata"]["namespace"],
                                     cmd)
    return result.split("\n")[0]


def get_macvlan_pod_events(client, pod, reason="MacvlanIPError", limit=1):
    pod_name = pod["metadata"]["name"]
    pod_ns = pod["metadata"]["namespace"]
    selector = f"involvedObject.name={pod_name},involvedObject.namespace={pod_ns},reason={reason}"
    return client.list_event(fieldSelector=selector, limit=limit).data


def get_pod_iproute(pod):
    cmd = "ip route"
    result = get_kubectl_exec_output(pod["metadata"]["name"],
                                     pod["metadata"]["namespace"],
                                     cmd)
    return result.split(" \n")


def get_ips_from_svc(cmd_pod, svc):
    svc_name = svc["metadata"]["name"]
    svc_ns = svc["metadata"]["namespace"]
    fqdn = f"{svc_name}.{svc_ns}.svc.cluster.local"
    cmd = "nslookup -type=a " + fqdn + " | awk '/^Address: / { print $2 }'"
    result = get_kubectl_exec_output(cmd_pod["metadata"]["name"],
                                     svc_ns,
                                     cmd)
    return list(filter(None, result.split("\n")))


def get_worker_nodes(client):
    nodes = client.list_node().data
    schedulable_nodes = []
    for node in nodes:
        if node["metadata"]["labels"]["node-role.kubernetes.io/master"] == "true":
            schedulable_nodes.append(node)
        elif node["metadata"]["labels"]["node-role.kubernetes.io/worker"] == "true":
            schedulable_nodes.append(node)
        elif node["metadata"]["labels"]["node.kubernetes.io/instance-type"] == "k3s":
            schedulable_nodes.append(node)

    return schedulable_nodes


def get_random_ips_from_cidr(cidr, count):
    net = ipaddress.IPv4Network(cidr)
    return list(map(str, random.sample(list(net.hosts())[1:-1], count)))


def get_random_macs(count):
    macs = []
    for i in range(count):
        e = "52:54:00:%02x:%02x:%02x" % tuple(random.randint(0, 255) for v in range(3))
        macs.append(e)
    return macs


def create_macvlansubnet(client, cidr, ranges=[], gateway="", routes=[], vlan=0,
                         pod_default_gateway={}, ipv6=False, delay_reuse=0):
    subnet = read_json_from_resource_dir("macvlan", "macvlan_subnet.json")
    subnet["metadata"]["name"] = random_test_name('test-macvlan')
    if ipv6:
        subnet["metadata"]["annotations"]["macvlan.panda.io/ipv6to4"] = "true"
    subnet["spec"]["master"] = DEFAULT_MASTER
    subnet["spec"]["cidr"] = cidr
    subnet["spec"]["ranges"] = ranges
    subnet["spec"]["gateway"] = gateway
    subnet["spec"]["routes"] = routes
    subnet["spec"]["podDefaultGateway"] = pod_default_gateway
    subnet["spec"]["delay_reuse"]= delay_reuse
    subnet["spec"]["vlan"] = vlan

    return client.create_macvlan_cluster_cattle_io_macvlansubnet(subnet)


def create_macvlan_service(client, ns, wl_label_v, ports, skip_wait=False):
    template = read_json_from_resource_dir("macvlan", "macvlan_service.json")

    template["spec"]["ports"] = ports
    template["spec"]["type"] = "ClusterIP"
    template["metadata"]["name"] = random_test_name('test-svc') + "-macvlan"
    template["metadata"]["namespace"] = ns["metadata"]["name"]
    template["metadata"]["annotations"]["k8s.v1.cni.cncf.io/networks"] ="static-macvlan-cni-attach"

    template["spec"]["selector"][wl_selector] = wl_label_v
    template["spec"]["clusterIP"] = "None"

    service = client.create_service(template)
    if not skip_wait:
        wait_for(lambda: client.reload(service).metadata.state.name == "active",
                    timeout_message="time out waiting for service to be ready")

    return client.reload(service)


def create_simple_service(client, ns, wl_label_v, ports, svctype="ClusterIP", name=None,
                          ownerref=None, headless=False, skip_wait=False):
    template = read_json_from_resource_dir("macvlan", "macvlan_service.json")

    if name is not None:
        template["metadata"]["name"] = name
    else:
        template["metadata"]["name"] = random_test_name('test-svc')
    template["metadata"]["namespace"] = ns["metadata"]["name"]
    if ownerref is not None:
        template["metadata"]["ownerReferences"].append(ownerref)
    template["spec"]["ports"] = ports
    template["spec"]["type"] = svctype
    template["spec"]["selector"][wl_selector] = wl_label_v
    if headless:
        template["spec"]["clusterIP"] = "None"

    service = client.create_service(template)
    if not skip_wait:
        wait_for(lambda: client.reload(service).metadata.state.name == "active",
                    timeout_message="time out waiting for service to be ready")

    return client.reload(service)


def create_macvlan_pod(client, ns, group, image, ip, mac, subnet, mode="dual", skip_wait=False):
    template = read_json_from_resource_dir("macvlan", "macvlan_pod.json")
    pod_name = random_test_name('test-macvlan-pod')
    template["metadata"]["name"] = pod_name
    template["metadata"]["namespace"] = ns["metadata"]["name"]
    template["metadata"]["labels"][wl_selector] = group
    template["spec"]["containers"][0]["image"] = image
    template["spec"]["containers"][0]["name"] = pod_name
    template["metadata"]["annotations"]["macvlan.pandaria.cattle.io/ip"] = ip
    template["metadata"]["annotations"]["macvlan.pandaria.cattle.io/mac"] = mac
    template["metadata"]["annotations"]["macvlan.pandaria.cattle.io/subnet"] = subnet

    if mode == "dual":
        template["metadata"]["annotations"][eth1_anno_key] = eth1_network
        del template["metadata"]["annotations"][eth0_anno_key]
    elif mode == "single":
        template["metadata"]["annotations"][eth0_anno_key] = eth0_network
        del template["metadata"]["annotations"][eth1_anno_key]

    pod = client.create_pod(template)
    if not skip_wait:
        wait_for(lambda: client.reload(pod).metadata != None and client.reload(pod).metadata.state.name == "running",
                 timeout_message="time out waiting for pod to be ready")

    return client.reload(pod)


def ip_in_subnet(ip, cidr):
    return ip in list(map(str, ipaddress.IPv4Network(cidr).hosts()))


def convert_ipv6_to_ipv4(ip):
    v6 = ipaddress.IPv6Address(ip)
    return str(v6.sixtofour)


def ping(pod, ip):
    cmd = "ping -w 5 " + ip
    result = get_kubectl_exec_code(pod["metadata"]["name"],
                                   pod["metadata"]["namespace"],
                                   cmd)
    return result
