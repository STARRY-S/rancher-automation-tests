import pytest

from .common import *  # NOQA

subnet_cidr = "192.168.10.0/24"
stop_old_strategy = {
    "rollingUpdate": {
        "maxSurge": 0,
        "maxUnavailable": "25%"
    },
    "type": "RollingUpdate"
}


def test_auto():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    busybox_workload = create_macvlan_deployment(subnet["metadata"]["name"],
                                                 "auto",
                                                 "auto",
                                                 1)

    busybox_pods = get_common_workload_pods(client, busybox_workload)
    assert len(busybox_pods) == 1

    pod_ip = get_macvlan_pod_ip(busybox_pods[0])
    assert ip_in_subnet(pod_ip, subnet["spec"]["cidr"])
    assert ip_in_subnet(pod_ip, "192.168.100.0/24") == False

    client.delete(busybox_workload)


def test_fixed_ip():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    expected_ips = get_random_ips_from_cidr(subnet["spec"]["cidr"], 2)
    busybox_workload = create_macvlan_deployment(subnet["metadata"]["name"],
                                                 '-'.join(expected_ips),
                                                 "auto",
                                                 2)

    busybox_pods = get_common_workload_pods(client, busybox_workload)
    assert len(busybox_pods) == 2

    for pod in busybox_pods:
        pod_ip = get_macvlan_pod_ip(pod)
        assert pod_ip in expected_ips
        expected_ips.remove(pod_ip)

    client.delete(busybox_workload)


def test_fixed_mac():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    expected_macs = get_random_macs(2)
    busybox_workload = create_macvlan_deployment(subnet["metadata"]["name"],
                                                 "auto",
                                                 "-".join(expected_macs),
                                                 2)

    busybox_pods = get_common_workload_pods(client, busybox_workload)
    assert len(busybox_pods) == 2

    for pod in busybox_pods:
        pod_mac = get_macvlan_pod_mac(pod)
        assert pod_mac in expected_macs
        expected_macs.remove(pod_mac)

    client.delete(busybox_workload)


def test_single_nic():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    busybox_workload = create_macvlan_deployment(subnet["metadata"]["name"],
                                                 "auto",
                                                 "auto",
                                                 1,
                                                 mode="single")

    busybox_pods = get_common_workload_pods(client, busybox_workload)
    assert len(busybox_pods) == 1

    pod_ip = get_macvlan_pod_ip(busybox_pods[0], nic="eth0")
    assert ip_in_subnet(pod_ip, subnet["spec"]["cidr"])
    assert ip_in_subnet(pod_ip, "192.168.100.0/24") == False

    client.delete(busybox_workload)


def test_upgrade():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    expected_ip = get_random_ips_from_cidr(subnet["spec"]["cidr"], 1)[0]
    old_workload = create_macvlan_deployment(subnet["metadata"]["name"],
                                                 expected_ip,
                                                 "auto",
                                                 1,
                                                 strategy=stop_old_strategy)
    old_pod = get_common_workload_pods(client, old_workload)[0]
    old_ip = get_macvlan_pod_ip(old_pod)
    assert old_ip == expected_ip

    old_workload.spec.template.metadata.annotations.test_upgrade = "true"
    new_workload = client.update(old_workload, old_workload)
    wait_for(lambda: client.reload(new_workload).metadata.state.name == "active",
             timeout_message="time out waiting for deployment to be ready")
    new_pod = get_common_workload_pods(client, new_workload)[0]
    new_ip = get_macvlan_pod_ip(new_pod)
    assert new_ip == expected_ip

    client.delete(new_workload)


def create_macvlan_deployment(subnet, ip, mac, replicas, strategy=None, mode="dual",
                              skip_wait=False):
    client = factory["client"]
    ns_name = factory['ns']["metadata"]["name"]
    name = random_test_name("busybox")
    template = read_json_from_resource_dir("macvlan", "macvlan_deployment.json")
    # set metadata
    template["metadata"]["name"] = name
    template["metadata"]["namespace"] = ns_name

    # set template
    spec = template["spec"]
    spec["template"]["spec"]["containers"][0]["image"] = BUSYBOX_IMAGE
    spec["template"]["spec"]["containers"][0]["name"] = name
    spec["template"]["metadata"]["annotations"]["macvlan.pandaria.cattle.io/ip"] = ip
    spec["template"]["metadata"]["annotations"]["macvlan.pandaria.cattle.io/mac"] = mac
    spec["template"]["metadata"]["annotations"]["macvlan.pandaria.cattle.io/subnet"] = subnet

    if strategy is not None:
        spec["strategy"] = strategy

    if mode == "dual":
        spec["template"]["metadata"]["annotations"][eth1_anno_key] = eth1_network
        del spec["template"]["metadata"]["annotations"][eth0_anno_key]
    elif mode == "single":
        spec["template"]["metadata"]["annotations"][eth0_anno_key] = eth0_network
        del spec["template"]["metadata"]["annotations"][eth1_anno_key]

    spec["replicas"] = replicas

    # set label and selector
    label_value = f"apps.deployment-{ns_name}-{name}"
    spec["template"]["metadata"]["labels"][wl_selector] = label_value
    spec["selector"]["matchLabels"][wl_selector] = label_value
    template["spec"] = spec

    deployment = client.create_apps_deployment(template)
    if not skip_wait:
        wait_for(lambda: client.reload(deployment).metadata.state.name == "active",
                    timeout_message="time out waiting for deployment to be ready")
    return client.reload(deployment)


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
