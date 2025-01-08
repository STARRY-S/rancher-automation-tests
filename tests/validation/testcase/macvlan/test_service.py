import pytest

from .test_deployment import create_macvlan_deployment
from .test_daemonset import create_macvlan_daemonset
from .test_statefulset import create_macvlan_statefulset
from .common import *  # NOQA


ownerref_deployment = {
    "apiVersion": "apps/v1",
    "controller": True,
    "kind": "Deployment",
    "name": "",
    "uid": ""
}
ownerref_daemonset = {
    "apiVersion": "apps/v1",
    "controller": True,
    "kind": "Daemonset",
    "name": "",
    "uid": ""
}
subnet_cidr = "192.168.11.0/24"
svc_ports = [{"name": "80tcp", "protocol": "TCP", "port": 80, "targetPort": 80}]


def test_deployment_auto():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    # create deployment and service
    busybox_workload = create_macvlan_deployment(subnet["metadata"]["name"],
                                                 "auto", "auto", 2, skip_wait=True)
    wl_name = busybox_workload["metadata"]["name"]
    wl_ns = busybox_workload["metadata"]["namespace"]
    label_value = f"apps.deployment-{wl_ns}-{wl_name}"
    ownerref = ownerref_deployment.copy()
    ownerref["name"] = wl_name
    ownerref["uid"] = busybox_workload["metadata"]["uid"]
    simple_svc = create_simple_service(client, ns, label_value, svc_ports, name=wl_name,
                                       ownerref=ownerref)
    wait_for(lambda: "readyReplicas" in client.reload(busybox_workload).status and \
             client.reload(busybox_workload).status.readyReplicas == 2,
             timeout_message="time out waiting for deployment to be ready")

    busybox_pods = get_common_workload_pods(client, busybox_workload)
    assert len(busybox_pods) == 2
    pod1_ip = get_macvlan_pod_ip(busybox_pods[0])
    pod2_ip = get_macvlan_pod_ip(busybox_pods[1])
    pod_ips = (pod1_ip, pod2_ip)

    # validate macvlan service by endpointslice
    macvlan_svc_name = simple_svc["metadata"]["name"] + "-macvlan"
    macvlan_svc_id = simple_svc["metadata"]["namespace"] + "/" + macvlan_svc_name
    macvlan_svc = client.by_id_service(macvlan_svc_id)
    assert macvlan_svc is not None

    time.sleep(1)

    label_selector = f"kubernetes.io/service-name={macvlan_svc_name}"
    ep_slices = client.list_discovery_k8s_io_endpointslice(labelSelector=label_selector).data
    assert len(ep_slices) == 1
    assert len(ep_slices[0].endpoints) == 2
    assert ep_slices[0].endpoints[0].addresses[0] in pod_ips
    assert ep_slices[0].endpoints[1].addresses[0] in pod_ips

    # validate macvlan service by fqdn
    assert sorted(get_ips_from_svc(busybox_pods[0], macvlan_svc)) == sorted(pod_ips)

    client.delete(busybox_workload)


def test_statefulset_auto():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    # create deployment and service
    busybox_workload = create_macvlan_statefulset(subnet["metadata"]["name"],
                                                 "auto", "auto", 2)
    wait_for(lambda: "readyReplicas" in client.reload(busybox_workload).status and \
             client.reload(busybox_workload).status.readyReplicas == 2,
             timeout_message="time out waiting for sts to be ready")

    busybox_pods = get_common_workload_pods(client, busybox_workload)
    assert len(busybox_pods) == 2
    pod1_ip = get_macvlan_pod_ip(busybox_pods[0])
    pod2_ip = get_macvlan_pod_ip(busybox_pods[1])
    pod_ips = (pod1_ip, pod2_ip)

    # validate macvlan service by endpointslice
    macvlan_svc_name = busybox_workload["metadata"]["name"] + "-macvlan"
    macvlan_svc_id = busybox_workload["metadata"]["namespace"] + "/" + macvlan_svc_name
    macvlan_svc = client.by_id_service(macvlan_svc_id)
    assert macvlan_svc is not None

    time.sleep(1)

    label_selector = f"kubernetes.io/service-name={macvlan_svc_name}"
    ep_slices = client.list_discovery_k8s_io_endpointslice(labelSelector=label_selector).data
    assert len(ep_slices) == 1
    assert len(ep_slices[0].endpoints) == 2
    assert ep_slices[0].endpoints[0].addresses[0] in pod_ips
    assert ep_slices[0].endpoints[1].addresses[0] in pod_ips

    # validate macvlan service by fqdn
    assert sorted(get_ips_from_svc(busybox_pods[0], macvlan_svc)) == sorted(pod_ips)

    client.delete(busybox_workload)


def test_daemonset_auto():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]
    worker_nodes = factory["worker_nodes"]

    # create deployment and service
    busybox_workload = create_macvlan_daemonset(subnet["metadata"]["name"],
                                                "auto", "auto", skip_wait=True)
    wl_name = busybox_workload["metadata"]["name"]
    wl_ns = busybox_workload["metadata"]["namespace"]
    label_value = f"apps.daemonset-{wl_ns}-{wl_name}"
    ownerref = ownerref_daemonset.copy()
    ownerref["name"] = wl_name
    ownerref["uid"] = busybox_workload["metadata"]["uid"]
    simple_svc = create_simple_service(client, ns, label_value, svc_ports, name=wl_name,
                                       ownerref=ownerref)
    wait_for(lambda: client.reload(busybox_workload).status.numberReady == len(worker_nodes),
             timeout_message="time out waiting for ds to be ready")

    busybox_pods = get_common_workload_pods(client, busybox_workload)
    assert len(busybox_pods) == len(worker_nodes)
    pod_ips = []
    for pod in busybox_pods:
        pod_ips.append(get_macvlan_pod_ip(pod))

    # validate macvlan service by endpointslice
    macvlan_svc_name = simple_svc["metadata"]["name"] + "-macvlan"
    macvlan_svc_id = simple_svc["metadata"]["namespace"] + "/" + macvlan_svc_name
    macvlan_svc = client.by_id_service(macvlan_svc_id)
    assert macvlan_svc is not None

    time.sleep(1)

    label_selector = f"kubernetes.io/service-name={macvlan_svc_name}"
    ep_slices = client.list_discovery_k8s_io_endpointslice(labelSelector=label_selector).data
    assert len(ep_slices) == 1
    # validate macvlan service by fqdn
    assert sorted(get_ips_from_svc(busybox_pods[0], macvlan_svc)) == sorted(pod_ips)

    client.delete(busybox_workload)


def test_unsupported_auto():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    group = "test-auto-svc"
    simple_svc = create_simple_service(client, ns, group, svc_ports)
    expected_ip = get_random_ips_from_cidr(subnet["spec"]["cidr"], 1)[0]
    pod = create_macvlan_pod(client, ns, group, BUSYBOX_IMAGE, expected_ip, "auto",
                             subnet["metadata"]["name"])

    macvlan_svc_name = simple_svc["metadata"]["name"] + "-macvlan"
    macvlan_svc_id = ns["metadata"]["name"] + "/" + macvlan_svc_name
    macvlan_svc = client.by_id_service(macvlan_svc_id)
    assert macvlan_svc is None

    client.delete(pod)
    client.delete(simple_svc)


def test_custom():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    group = "test-custom-svc"
    expected_ip = get_random_ips_from_cidr(subnet["spec"]["cidr"], 1)[0]
    macvlan_svc = create_macvlan_service(client, ns, group, svc_ports)
    pod = create_macvlan_pod(client, ns, group, BUSYBOX_IMAGE, expected_ip, "auto",
                             subnet["metadata"]["name"])
    macvlan_svc_name = macvlan_svc["metadata"]["name"]

    time.sleep(1)

    label_selector = f"kubernetes.io/service-name={macvlan_svc_name}"
    ep_slices = client.list_discovery_k8s_io_endpointslice(labelSelector=label_selector).data
    assert len(ep_slices) == 1
    assert len(ep_slices[0].endpoints) == 1
    assert ep_slices[0].endpoints[0].addresses[0] == expected_ip

    client.delete(pod)
    client.delete(macvlan_svc)


@pytest.fixture(scope='module', autouse="True")
def setup_module(request):
    cluster = factory["cluster"]
    project = create_project(factory["v3_admin_client"],
                             cluster,
                             random_test_name("project"))
    factory["project"] = project
    ns = create_ns_v1(cluster.id, project, random_test_name("ns"))
    factory["ns"] = ns
    vlan = random.randint(0, 1024)
    factory["subnet"] = create_macvlansubnet(factory["client"], subnet_cidr, vlan=vlan)

    def fin():
        client = factory["client"]
        cluster = factory['cluster']
        ns = factory['ns']
        delete_ns_v1(cluster.id, ns["metadata"]["name"])
        client.delete(factory["project"])
        client.delete(factory["subnet"])
    request.addfinalizer(fin)
