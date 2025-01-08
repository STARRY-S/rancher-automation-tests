import pytest

from .common import *  # NOQA

subnet_cidr = "192.168.15.0/24"
svc_ports = [{"name": "80tcp", "protocol": "TCP", "port": 80, "targetPort": 80}]


def test_auto():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    ordered_workload = create_macvlan_statefulset(subnet["metadata"]["name"],
                                                 "auto",
                                                 "auto",
                                                 2)

    ordered_pods = get_common_workload_pods(client, ordered_workload)
    assert len(ordered_pods) == 2

    for pod in ordered_pods:
        pod_ip = get_macvlan_pod_ip(pod)
        assert ip_in_subnet(pod_ip, subnet["spec"]["cidr"])

    client.delete(ordered_workload)


    parallel_workload = create_macvlan_statefulset(subnet["metadata"]["name"],
                                                   "auto",
                                                   "auto",
                                                   2,
                                                   parallel=True)
    parallel_pods = get_common_workload_pods(client, parallel_workload)
    assert len(parallel_pods) == 2

    for pod in parallel_pods:
        pod_ip = get_macvlan_pod_ip(pod)
        assert ip_in_subnet(pod_ip, subnet["spec"]["cidr"])

    client.delete(parallel_workload)


def test_fixed_ip():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    expected_ips = get_random_ips_from_cidr(subnet["spec"]["cidr"], 2)
    ordered_workload = create_macvlan_statefulset(subnet["metadata"]["name"],
                                                 "-".join(expected_ips),
                                                 "auto",
                                                 2)

    ordered_pods = get_common_workload_pods(client, ordered_workload)
    assert len(ordered_pods) == 2

    for pod in ordered_pods:
        pod_ip = get_macvlan_pod_ip(pod)
        assert pod_ip in expected_ips
        expected_ips.remove(pod_ip)

    client.delete(ordered_workload)

    time.sleep(0.5)
    expected_ips = get_random_ips_from_cidr(subnet["spec"]["cidr"], 2)
    parallel_workload = create_macvlan_statefulset(subnet["metadata"]["name"],
                                                   "-".join(expected_ips),
                                                   "auto",
                                                   2,
                                                   parallel=True)
    parallel_pods = get_common_workload_pods(client, parallel_workload)
    assert len(parallel_pods) == 2

    for pod in parallel_pods:
        pod_ip = get_macvlan_pod_ip(pod)
        assert pod_ip in expected_ips
        expected_ips.remove(pod_ip)

    client.delete(parallel_workload)


def test_fixed_mac():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    expected_macs = get_random_macs(2)
    ordered_workload = create_macvlan_statefulset(subnet["metadata"]["name"],
                                                 "auto",
                                                 "-".join(expected_macs),
                                                 2)

    ordered_pods = get_common_workload_pods(client, ordered_workload)
    assert len(ordered_pods) == 2

    for pod in ordered_pods:
        pod_mac = get_macvlan_pod_mac(pod)
        assert pod_mac in expected_macs
        expected_macs.remove(pod_mac)

    client.delete(ordered_workload)

    expected_macs = get_random_macs(2)
    parallel_workload = create_macvlan_statefulset(subnet["metadata"]["name"],
                                                   "auto",
                                                   "-".join(expected_macs),
                                                   2,
                                                   parallel=True)
    parallel_pods = get_common_workload_pods(client, parallel_workload)
    assert len(parallel_pods) == 2

    for pod in parallel_pods:
        pod_mac = get_macvlan_pod_mac(pod)
        assert pod_mac in expected_macs
        expected_macs.remove(pod_mac)

    client.delete(parallel_workload)


def test_single_nic():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    ordered_workload = create_macvlan_statefulset(subnet["metadata"]["name"],
                                                  "auto",
                                                  "auto",
                                                  2,
                                                  mode="single")

    ordered_pods = get_common_workload_pods(client, ordered_workload)
    assert len(ordered_pods) == 2

    for pod in ordered_pods:
        pod_ip = get_macvlan_pod_ip(pod, nic="eth0")
        assert ip_in_subnet(pod_ip, subnet["spec"]["cidr"])

    client.delete(ordered_workload)


    parallel_workload = create_macvlan_statefulset(subnet["metadata"]["name"],
                                                   "auto",
                                                   "auto",
                                                   2,
                                                   parallel=True,
                                                   mode="single")
    parallel_pods = get_common_workload_pods(client, parallel_workload)
    assert len(parallel_pods) == 2

    for pod in parallel_pods:
        pod_ip = get_macvlan_pod_ip(pod, nic="eth0")
        assert ip_in_subnet(pod_ip, subnet["spec"]["cidr"])

    client.delete(parallel_workload)


def test_ordered_upgrade():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    expected_ip = get_random_ips_from_cidr(subnet["spec"]["cidr"], 1)[0]
    old_workload = create_macvlan_statefulset(subnet["metadata"]["name"],
                                              expected_ip,
                                              "auto",
                                              1)
    old_pod = get_common_workload_pods(client, old_workload)[0]
    old_ip = get_macvlan_pod_ip(old_pod)
    assert old_ip == expected_ip

    old_workload.spec.template.metadata.annotations.test_upgrade = "true"
    new_workload = client.update(old_workload, old_workload)
    wait_for(lambda: client.reload(new_workload).metadata.state.name == "active",
             timeout_message="time out waiting for statefulset to be ready")
    new_pod = get_common_workload_pods(client, new_workload)[0]
    new_ip = get_macvlan_pod_ip(new_pod)
    assert new_ip == expected_ip

    client.delete(new_workload)


def test_parallel_upgrade():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    expected_ips = get_random_ips_from_cidr(subnet["spec"]["cidr"], 3)
    old_workload = create_macvlan_statefulset(subnet["metadata"]["name"],
                                              "-".join(expected_ips),
                                              "auto",
                                              3,
                                              parallel=True)
    old_ips = []
    for pod in get_common_workload_pods(client, old_workload):
        old_ips.append(get_macvlan_pod_ip(pod))
    assert sorted(old_ips) == sorted(expected_ips)

    old_workload.spec.template.metadata.annotations.test_upgrade = "true"
    new_workload = client.update(old_workload, old_workload)
    wait_for(lambda: client.reload(new_workload).metadata.state.name == "active",
             timeout_message="time out waiting for statefulset to be ready")
    new_ips = []
    for pod in get_common_workload_pods(client, new_workload):
        new_ips.append(get_macvlan_pod_ip(pod))
    assert sorted(new_ips) == sorted(expected_ips)

    client.delete(new_workload)


def create_statefulset_service(wl_name):
    client = factory["client"]
    ns = factory["ns"]
    ns_name = ns["metadata"]["name"]

    label_value = f"apps.statefulset-{ns_name}-{wl_name}"
    return create_simple_service(client, ns, label_value, svc_ports, name=wl_name, headless=True)


def create_macvlan_statefulset(subnet, ip, mac, replicas, parallel=False,
                               mode="dual", skip_wait=False):
    client = factory["client"]
    ns = factory["ns"]
    ns_name = ns["metadata"]["name"]

    name = random_test_name("busybox")
    sts_service = create_statefulset_service(name)

    template = read_json_from_resource_dir("macvlan", "macvlan_statefulset.json")
    # set metadata
    template["metadata"]["name"] = name
    template["metadata"]["namespace"] = ns_name

    spec = template["spec"]
    spec["serviceName"] = sts_service["metadata"]["name"]
    if parallel:
        spec["podManagementPolicy"] = "Parallel"

    # set template
    spec["template"]["spec"]["containers"][0]["image"] = BUSYBOX_IMAGE
    spec["template"]["spec"]["containers"][0]["name"] = name
    spec["template"]["metadata"]["annotations"]["macvlan.pandaria.cattle.io/ip"] = ip
    spec["template"]["metadata"]["annotations"]["macvlan.pandaria.cattle.io/mac"] = mac
    spec["template"]["metadata"]["annotations"]["macvlan.pandaria.cattle.io/subnet"] = subnet

    if mode == "dual":
        spec["template"]["metadata"]["annotations"][eth1_anno_key] = eth1_network
        del spec["template"]["metadata"]["annotations"][eth0_anno_key]
    elif mode == "single":
        spec["template"]["metadata"]["annotations"][eth0_anno_key] = eth0_network
        del spec["template"]["metadata"]["annotations"][eth1_anno_key]

    spec["replicas"] = replicas

    # set label and selector
    label_value = f"apps.statefulset-{ns_name}-{name}"
    spec["template"]["metadata"]["labels"][wl_selector] = label_value
    spec["selector"]["matchLabels"][wl_selector] = label_value
    template["spec"] = spec

    sts = client.create_apps_statefulset(template)
    if not skip_wait:
        wait_for(lambda: client.reload(sts).metadata.state.name == "active",
                 timeout_message="time out waiting for statefulset to be ready")
    return client.reload(sts)


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
