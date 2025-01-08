import pytest

from .test_deployment import create_flatnetwork_deployment
from .common import *  # NOQA


def test_ip_ranges():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.60.0/24"
    ranges = [
        {
            "from": "192.168.60.100",
            "to": "192.168.60.101"
        },
        {
            "from": "192.168.60.110",
            "to": "192.168.60.111"
        }
    ]
    expected_ips = ["192.168.60.100", "192.168.60.101", "192.168.60.110", "192.168.60.111"]
    subnet = create_flatnetwork_subnet(
        client,
        cidr,
        ranges=ranges)
    busybox_workload = create_flatnetwork_deployment(subnet["metadata"]["name"],
                                                 "auto",
                                                 "auto",
                                                 len(expected_ips))
    busybox_pods = get_common_workload_pods(client, busybox_workload)
    assert len(busybox_pods) == len(expected_ips)

    for pod in busybox_pods:
        pod_ip = get_flatnetwork_pod_ip(pod)
        assert pod_ip in expected_ips
        expected_ips.remove(pod_ip)

    client.delete(busybox_workload)
    client.delete(subnet)


def test_route_settings():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.61.0/24"
    route_settings = {
        "addClusterCIDR": True,
        "addServiceCIDR": True,
        "addNodeCIDR": True,
        "addPodIPToHost": True,
        "flatNetworkDefaultGateway": True,
    }
    gateway = "192.168.61.254"
    subnet = create_flatnetwork_subnet(client, cidr,
                                  gateway=gateway,
                                  route_settings=route_settings)
    pod = create_flatnetwork_pod(client, ns, "test-gateway", BUSYBOX_IMAGE, "auto", "auto",
                             subnet["metadata"]["name"])

    routes = get_pod_iproute(pod)
    validated = False
    for r in routes:
        if 'default' in r:
            validated = True
            assert "default via 192.168.61.254 dev eth1" in r
            break
    client.delete(pod)
    assert validated

    # validate https://github.com/cnrancher/pandaria/issues/2445
    pod = create_flatnetwork_pod(client, ns, "test-gateway", BUSYBOX_IMAGE, "auto", "auto",
                             subnet["metadata"]["name"], mode="single")
    routes = get_pod_iproute(pod)
    validated = False
    for r in routes:
        if '192.168.61' in r:
            validated = True
            assert "192.168.61.0/24 dev eth0" in r
            break
    client.delete(pod)
    client.delete(subnet)
    assert validated


def test_routes():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.62.0/24"
    gateway = "192.168.62.254"
    routes = [
        {
            "dev": "eth1",
            "dst": "99.88.77.0/24",
            "gw": "192.168.62.254",
        }
    ]
    subnet = create_flatnetwork_subnet(client, cidr,
                                  gateway=gateway,
                                  routes=routes)
    pod = create_flatnetwork_pod(client, ns, "test-routes", BUSYBOX_IMAGE, "auto", "auto",
                             subnet["metadata"]["name"])

    routes = get_pod_iproute(pod)
    print('routes:', routes)
    validated = False
    for r in routes:
        if '99.88.77.0/24' in r:
            validated = True
            assert "99.88.77.0/24 via 192.168.62.254 dev eth1" in r
            break
    assert validated
    client.delete(pod)
    client.delete(subnet)


def test_ipv6to4():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.63.0/24"
    ranges = [
        {
            "from": "192.168.63.10",
            "to": "192.168.63.100"
        }
    ]
    subnet = create_flatnetwork_subnet(client, cidr, ranges=ranges, ipv6to4=True)
    pod = create_flatnetwork_pod(client, ns, "test-ipv6", BUSYBOX_IMAGE, "auto", "auto",
                             subnet["metadata"]["name"])
    pod_ipv4 = get_flatnetwork_pod_ip(pod)
    pod_ipv6 = get_flatnetwork_pod_ip(pod, ipv6=True)
    assert pod_ipv4 == convert_ipv6_to_ipv4(pod_ipv6)
    client.delete(pod)
    client.delete(subnet)


def test_vlan():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    # validate same vlan
    cidr = "192.168.65.0/24"
    vlan = 1001
    ranges = [
        {
            "from": "192.168.65.10",
            "to": "192.168.65.100"
        }
    ]
    subnet = create_flatnetwork_subnet(client, cidr, ranges=ranges, vlan=vlan)
    pod_a = create_flatnetwork_pod(client, ns, "test-vlan", BUSYBOX_IMAGE, "auto", "auto",
                               subnet["metadata"]["name"])
    pod_b = create_flatnetwork_pod(client, ns, "test-vlan", BUSYBOX_IMAGE, "auto", "auto",
                               subnet["metadata"]["name"])
    pod_b_ip = get_flatnetwork_pod_ip(pod_b)
    assert ping(pod_a, pod_b_ip) == 0

    # validate different vlan
    diff_vlan = 1002
    diff_subnet = create_flatnetwork_subnet(client, cidr, vlan=diff_vlan)
    pod_c_ip = "192.168.65.250"
    pod_c = create_flatnetwork_pod(client, ns, "test-vlan", BUSYBOX_IMAGE, pod_c_ip, "auto",
                               diff_subnet["metadata"]["name"])
    assert get_flatnetwork_pod_ip(pod_c) == pod_c_ip
    assert ping(pod_a, pod_c_ip) == 1

    client.delete(pod_a)
    client.delete(pod_b)
    client.delete(pod_c)
    client.delete(subnet)
    client.delete(diff_subnet)


@pytest.fixture(scope='module', autouse="True")
def setup_module(request):
    cluster = factory["cluster"]
    project = create_project(factory["v3_admin_client"],
                             cluster,
                             random_test_name("project"))
    factory["project"] = project
    ns = create_ns_v1(cluster.id, project, random_test_name("ns"))
    factory["ns"] = ns

    def fin():
        client = factory["client"]
        cluster = factory['cluster']
        ns = factory['ns']
        delete_ns_v1(cluster.id, ns["metadata"]["name"])
        client.delete(factory["project"])
    request.addfinalizer(fin)
