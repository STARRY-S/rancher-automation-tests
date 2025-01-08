import pytest

from .common import *  # NOQA

subnet_cidr = "192.168.13.0/24"


def test_auto():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]
    worker_nodes = factory["worker_nodes"]

    busybox_workload = create_flatnetwork_daemonset(subnet["metadata"]["name"],
                                                "auto",
                                                "auto")
    busybox_pods = get_common_workload_pods(client, busybox_workload)
    assert len(busybox_pods) == len(worker_nodes)

    wait_for(lambda: client.reload(busybox_workload).status.numberReady == len(worker_nodes),
             timeout_message="time out waiting for ds to be ready")
    for pod in busybox_pods:
        pod_ip = get_flatnetwork_pod_ip(pod)
        assert ip_in_subnet(pod_ip, subnet["spec"]["cidr"])
        assert ip_in_subnet(pod_ip, "192.168.100.0/24") == False

    client.delete(busybox_workload)


def test_fixed_ip():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]
    worker_nodes = factory["worker_nodes"]

    expected_ips = get_random_ips_from_cidr(subnet["spec"]["cidr"], len(worker_nodes))
    busybox_workload = create_flatnetwork_daemonset(subnet["metadata"]["name"],
                                                '-'.join(expected_ips),
                                                "auto")
    wait_for(lambda: client.reload(busybox_workload).status.numberReady == len(worker_nodes),
             timeout_message="time out waiting for ds to be ready")
    busybox_pods = get_common_workload_pods(client, busybox_workload)
    assert len(busybox_pods) == len(worker_nodes)
    for pod in busybox_pods:
        pod_ip = get_flatnetwork_pod_ip(pod)
        assert pod_ip in expected_ips
        expected_ips.remove(pod_ip)

    client.delete(busybox_workload)


def test_fixed_mac():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]
    worker_nodes = factory["worker_nodes"]

    expected_macs = get_random_macs(len(worker_nodes))
    busybox_workload = create_flatnetwork_daemonset(subnet["metadata"]["name"],
                                                "auto",
                                                '-'.join(expected_macs))
    busybox_pods = get_common_workload_pods(client, busybox_workload)
    assert len(busybox_pods) == len(worker_nodes)

    wait_for(lambda: client.reload(busybox_workload).status.numberReady == len(worker_nodes),
             timeout_message="time out waiting for ds to be ready")
    for pod in busybox_pods:
        pod_mac = get_flatnetwork_pod_mac(pod)
        assert pod_mac in expected_macs
        expected_macs.remove(pod_mac)

    client.delete(busybox_workload)


def test_single_nic():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]
    worker_nodes = factory["worker_nodes"]

    busybox_workload = create_flatnetwork_daemonset(subnet["metadata"]["name"],
                                                "auto",
                                                "auto",
                                                mode="single")
    wait_for(lambda: client.reload(busybox_workload).status.numberReady == len(worker_nodes),
             timeout_message="time out waiting for ds to be ready")
    busybox_pods = get_common_workload_pods(client, busybox_workload)
    assert len(busybox_pods) == len(worker_nodes)

    for pod in busybox_pods:
        pod_ip = get_flatnetwork_pod_ip(pod, nic="eth0")
        assert ip_in_subnet(pod_ip, subnet["spec"]["cidr"])
        assert ip_in_subnet(pod_ip, "192.168.100.0/24") == False

    client.delete(busybox_workload)


def test_upgrade():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]
    worker_nodes = factory["worker_nodes"]

    expected_ips = get_random_ips_from_cidr(subnet["spec"]["cidr"], len(worker_nodes))
    old_workload = create_flatnetwork_daemonset(subnet["metadata"]["name"],
                                            '-'.join(expected_ips),
                                            "auto")
    wait_for(lambda: client.reload(old_workload).status.numberReady == len(worker_nodes),
             timeout_message="time out waiting for ds to be ready")
    old_pods = get_common_workload_pods(client, old_workload)
    old_ips = []
    for pod in get_common_workload_pods(client, old_workload):
        old_ips.append(get_flatnetwork_pod_ip(pod))
    assert sorted(old_ips) == sorted(expected_ips)

    old_workload = client.reload(old_workload)
    old_workload.spec.template.metadata.annotations.test_upgrade = "true"
    new_workload = client.update(old_workload, old_workload)
    wait_for(lambda: client.reload(new_workload).status.numberReady == len(worker_nodes),
             timeout_message="time out waiting for ds to be ready")
    new_ips = []
    for pod in get_common_workload_pods(client, new_workload):
        new_ips.append(get_flatnetwork_pod_ip(pod))
    assert sorted(new_ips) == sorted(expected_ips)

    client.delete(new_workload)


def create_flatnetwork_daemonset(subnet, ip, mac, mode="dual", skip_wait=False):
    client = factory["client"]
    ns_name = factory["ns"]["metadata"]["name"]
    name = random_test_name("busybox")
    template = read_json_from_resource_dir("flatnetwork", "daemonset.json")
    # set metadata
    template["metadata"]["name"] = name
    template["metadata"]["namespace"] = ns_name

    # set template
    spec = template["spec"]
    spec["template"]["spec"]["containers"][0]["image"] = BUSYBOX_IMAGE
    spec["template"]["spec"]["containers"][0]["name"] = name
    spec["template"]["metadata"]["annotations"]["flatnetwork.pandaria.io/ip"] = ip
    spec["template"]["metadata"]["annotations"]["flatnetwork.pandaria.io/mac"] = mac
    spec["template"]["metadata"]["annotations"]["flatnetwork.pandaria.io/subnet"] = subnet

    if mode == "dual":
        spec["template"]["metadata"]["annotations"][eth1_anno_key] = eth1_network
        del spec["template"]["metadata"]["annotations"][eth0_anno_key]
    elif mode == "single":
        spec["template"]["metadata"]["annotations"][eth0_anno_key] = eth0_network
        del spec["template"]["metadata"]["annotations"][eth1_anno_key]

    # set label and selector
    label_value = f"apps.daemonset-{ns_name}-{name}"
    spec["template"]["metadata"]["labels"][wl_selector] = label_value
    spec["selector"]["matchLabels"][wl_selector] = label_value
    template["spec"] = spec

    daemonset = client.create_apps_daemonset(template)
    if not skip_wait:
        wait_for(lambda: client.reload(daemonset).metadata.state.name == "active",
                    timeout_message="time out waiting for daemonset to be ready")
    return client.reload(daemonset)


@pytest.fixture(scope='module', autouse="True")
def setup_module(request):
    cluster = factory["cluster"]
    project = create_project(factory["v3_admin_client"],
                             cluster,
                             random_test_name("project"))
    factory["project"] = project
    ns = create_ns_v1(cluster.id, project, random_test_name("ns"))
    factory["ns"] = ns
    vlan = random.randint(2, 1024)
    factory["subnet"] = create_flatnetwork_subnet(
        factory["client"],
        subnet_cidr,
        vlan=vlan)

    time.sleep(1)

    def fin():
        client = factory["client"]
        cluster = factory['cluster']
        ns = factory['ns']
        delete_ns_v1(cluster.id, ns["metadata"]["name"])
        client.delete(factory["project"])
        client.delete(factory["subnet"])
    request.addfinalizer(fin)
