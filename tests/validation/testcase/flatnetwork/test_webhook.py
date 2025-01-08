import pytest

from .test_deployment import create_flatnetwork_deployment
from .test_daemonset import create_flatnetwork_daemonset
from .test_statefulset import create_flatnetwork_statefulset
from .test_job import create_flatnetwork_job
from .common import *  # NOQA


def test_routes_in_subnet():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.70.0/24"
    gateway = "192.168.70.254"
    routes = [
        {
            "dev": "eth1",
            "dst": "99.88.77.0/24",
            "via": "192.168.170.254",
        }
    ]
    try:
        subnet = create_flatnetwork_subnet(client, cidr, gateway=gateway, routes=routes)
        assert subnet is None
    except ApiError as e:
        assert e.error.status == 400
        assert "invalid gateway ip" in e.error.message


def test_pod_pending():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.70.0/24"
    subnet = create_flatnetwork_subnet(client, cidr)

    ip = "192.168.70.100"
    pre_pod = create_flatnetwork_pod(client, ns, "test-pod-pending", BUSYBOX_IMAGE, ip, "auto",
                             subnet["metadata"]["name"])
    assert pre_pod is not None
    post_pod = create_flatnetwork_pod(client, ns, "test-pod-pending", BUSYBOX_IMAGE, ip, "auto",
                                  subnet["metadata"]["name"], skip_wait=True)
    time.sleep(3)
    event = get_flatnetwork_pod_events(client, post_pod, limit=1)[0]
    # no available IP address
    assert ip in event.message

    client.delete(pre_pod)
    client.delete(post_pod)
    client.delete(subnet)


def test_deployment_ip():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.71.0/24"
    subnet = create_flatnetwork_subnet(client, cidr)

    # validate ip syntax
    try:
        ips = "192-168.71.10,"
        check = create_flatnetwork_deployment(subnet["metadata"]["name"], ips, "auto", 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate duplicate ips
    try:
        ips = "192.168.71.100-192.168.71.100"
        check = create_flatnetwork_deployment(subnet["metadata"]["name"], ips, "auto", 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate ips in subnet
    try:
        ips = "192.168.171.100-192.168.171.101"
        check = create_flatnetwork_deployment(subnet["metadata"]["name"], ips, "auto", 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate reserved ips
    try:
        ips = "-".join(get_random_ips_from_cidr(subnet["spec"]["cidr"], 2))
        pre_w = create_flatnetwork_deployment(subnet["metadata"]["name"]+'-1', ips, "auto", 0)
        assert pre_w is not None
        time.sleep(3)
        post_w = create_flatnetwork_deployment(subnet["metadata"]["name"]+'-2', ips, "auto", 0)
        assert post_w is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate used ips
    try:
        ip = get_random_ips_from_cidr(subnet["spec"]["cidr"], 1)[0]
        pod = create_flatnetwork_pod(client, ns, "test-deployment-ip", BUSYBOX_IMAGE, ip, "auto",
                                 subnet["metadata"]["name"])
        assert pod is not None
        time.sleep(3)
        post_w = create_flatnetwork_deployment(subnet["metadata"]["name"], ip, "auto", 0)
        assert post_w is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    client.delete(subnet)


def test_deployment_mac():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.72.0/24"
    subnet = create_flatnetwork_subnet(client, cidr)

    # validate mac syntax
    try:
        mac = "888888:1a:ff:e5:d8:05"
        check = create_flatnetwork_deployment(subnet["metadata"]["name"], "auto", mac, 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate single fixed mac and multiple ips
    try:
        mac = get_random_macs(1)[0]
        ips = "-".join(get_random_ips_from_cidr(subnet["spec"]["cidr"], 2))
        check = create_flatnetwork_deployment(subnet["metadata"]["name"], ips, mac, 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate multiple fixed ips and macs
    try:
        macs = "-".join(get_random_macs(3))
        ips = "-".join(get_random_ips_from_cidr(subnet["spec"]["cidr"], 2))
        check = create_flatnetwork_deployment(subnet["metadata"]["name"], ips, macs, 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate duplicate macs
    try:
        macs = "82:1a:ff:e5:d8:05-82:1a:ff:e5:d8:05"
        check = create_flatnetwork_deployment(subnet["metadata"]["name"], "auto", macs, 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate used macs
    try:
        mac = get_random_macs(1)[0]
        pod = create_flatnetwork_pod(client, ns, "test-deployment-mac", BUSYBOX_IMAGE, "auto", mac,
                                 subnet["metadata"]["name"])
        assert pod is not None
        time.sleep(3)
        post_w = create_flatnetwork_deployment(subnet["metadata"]["name"], "auto", mac, 0)
        assert post_w is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    client.delete(subnet)


def test_statefulset_ip():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.73.0/24"
    subnet = create_flatnetwork_subnet(client, cidr)

    # validate ip syntax
    try:
        ips = "192-168.73.10,"
        check = create_flatnetwork_statefulset(subnet["metadata"]["name"], ips, "auto", 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate duplicate ips
    try:
        ips = "192.168.73.100-192.168.73.100"
        check = create_flatnetwork_statefulset(subnet["metadata"]["name"], ips, "auto", 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate ips in subnet
    try:
        ips = "192.168.173.100-192.168.173.101"
        check = create_flatnetwork_statefulset(subnet["metadata"]["name"], ips, "auto", 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate reserved ips
    try:
        ips = "-".join(get_random_ips_from_cidr(subnet["spec"]["cidr"], 2))
        pre_w = create_flatnetwork_statefulset(subnet["metadata"]["name"], ips, "auto", 0)
        assert pre_w is not None
        time.sleep(3)
        post_w = create_flatnetwork_statefulset(subnet["metadata"]["name"], ips, "auto", 0)
        assert post_w is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate used ips
    try:
        ip = get_random_ips_from_cidr(subnet["spec"]["cidr"], 1)[0]
        pod = create_flatnetwork_pod(client, ns, "test-sts-ip", BUSYBOX_IMAGE, ip, "auto",
                                 subnet["metadata"]["name"])
        assert pod is not None
        time.sleep(3)
        check = create_flatnetwork_statefulset(subnet["metadata"]["name"], ip, "auto", 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    client.delete(subnet)


def test_statefulset_mac():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.74.0/24"
    subnet = create_flatnetwork_subnet(client, cidr)

    # validate mac syntax
    try:
        mac = "888888:1a:ff:e5:d8:05"
        check = create_flatnetwork_statefulset(subnet["metadata"]["name"], "auto", mac, 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate single fixed mac and multiple ips
    try:
        mac = get_random_macs(1)[0]
        ips = "-".join(get_random_ips_from_cidr(subnet["spec"]["cidr"], 2))
        check = create_flatnetwork_statefulset(subnet["metadata"]["name"], ips, mac, 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate multiple fixed ips and macs
    try:
        macs = "-".join(get_random_macs(3))
        ips = "-".join(get_random_ips_from_cidr(subnet["spec"]["cidr"], 2))
        check = create_flatnetwork_statefulset(subnet["metadata"]["name"], ips, macs, 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate duplicate macs
    try:
        macs = "82:1a:ff:e5:d8:05-82:1a:ff:e5:d8:05"
        check = create_flatnetwork_statefulset(subnet["metadata"]["name"], "auto", macs, 0)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate used macs
    try:
        mac = get_random_macs(1)[0]
        pod = create_flatnetwork_pod(client, ns, "test-deployment-mac", BUSYBOX_IMAGE, "auto", mac,
                                 subnet["metadata"]["name"])
        assert pod is not None
        time.sleep(3)
        post_w = create_flatnetwork_statefulset(subnet["metadata"]["name"], "auto", mac, 0)
        assert post_w is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    client.delete(subnet)


def test_daemonset_ip():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.75.0/24"
    subnet = create_flatnetwork_subnet(client, cidr)

    # validate ip syntax
    try:
        ips = "192-168.75.10,"
        check = create_flatnetwork_daemonset(subnet["metadata"]["name"], ips, "auto")
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate duplicate ips
    try:
        ips = "192.168.75.100-192.168.75.100"
        check = create_flatnetwork_daemonset(subnet["metadata"]["name"], ips, "auto")
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate ips in subnet
    try:
        ips = "192.168.175.100-192.168.175.101"
        check = create_flatnetwork_daemonset(subnet["metadata"]["name"], ips, "auto")
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate reserved ips
    try:
        ips = "-".join(get_random_ips_from_cidr(subnet["spec"]["cidr"], 2))
        pre_w = create_flatnetwork_deployment(subnet["metadata"]["name"], ips, "auto", 0)
        assert pre_w is not None
        time.sleep(3)
        check = create_flatnetwork_daemonset(subnet["metadata"]["name"], ips, "auto")
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate used ips
    try:
        ip = get_random_ips_from_cidr(subnet["spec"]["cidr"], 1)[0]
        pod = create_flatnetwork_pod(client, ns, "test-ds-ip", BUSYBOX_IMAGE, ip, "auto",
                                 subnet["metadata"]["name"])
        assert pod is not None
        time.sleep(3)
        check = create_flatnetwork_daemonset(subnet["metadata"]["name"], ip, "auto")
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    client.delete(subnet)


def test_daemonset_mac():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.76.0/24"
    subnet = create_flatnetwork_subnet(client, cidr)

    # validate mac syntax
    try:
        mac = "888888:1a:ff:e5:d8:05"
        check = create_flatnetwork_daemonset(subnet["metadata"]["name"], "auto", mac)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate single fixed mac and multiple ips
    try:
        mac = get_random_macs(1)[0]
        ips = "-".join(get_random_ips_from_cidr(subnet["spec"]["cidr"], 2))
        check = create_flatnetwork_daemonset(subnet["metadata"]["name"], ips, mac)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate multiple fixed ips and macs
    try:
        macs = "-".join(get_random_macs(3))
        ips = "-".join(get_random_ips_from_cidr(subnet["spec"]["cidr"], 2))
        check = create_flatnetwork_daemonset(subnet["metadata"]["name"], ips, macs)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate duplicate macs
    try:
        macs = "82:1a:ff:e5:d8:05-82:1a:ff:e5:d8:05"
        check = create_flatnetwork_daemonset(subnet["metadata"]["name"], "auto", macs)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate used macs
    try:
        mac = get_random_macs(1)[0]
        pod = create_flatnetwork_pod(client, ns, "test-ds-mac", BUSYBOX_IMAGE, "auto", mac,
                                 subnet["metadata"]["name"])
        assert pod is not None
        time.sleep(3)
        post_w = create_flatnetwork_daemonset(subnet["metadata"]["name"], "auto", mac)
        assert post_w is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    client.delete(subnet)


def test_job_ip():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.77.0/24"
    subnet = create_flatnetwork_subnet(client, cidr)

    # validate ip syntax
    try:
        ips = "192-168.77.10,"
        check = create_flatnetwork_job(subnet["metadata"]["name"], ips, "auto")
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate duplicate ips
    try:
        ips = "192.168.77.100-192.168.77.100"
        check = create_flatnetwork_job(subnet["metadata"]["name"], ips, "auto")
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate ips in subnet
    try:
        ips = "192.168.177.100-192.168.177.101"
        check = create_flatnetwork_job(subnet["metadata"]["name"], ips, "auto")
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate reserved ips
    try:
        ips = "-".join(get_random_ips_from_cidr(subnet["spec"]["cidr"], 2))
        pre_w = create_flatnetwork_job(subnet["metadata"]["name"], ips, "auto", 0)
        assert pre_w is not None
        time.sleep(3)
        check = create_flatnetwork_job(subnet["metadata"]["name"], ips, "auto")
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate used ips
    try:
        ip = get_random_ips_from_cidr(subnet["spec"]["cidr"], 1)[0]
        pod = create_flatnetwork_pod(client, ns, "test-job-ip", BUSYBOX_IMAGE, ip, "auto",
                                 subnet["metadata"]["name"])
        assert pod is not None
        time.sleep(3)
        check = create_flatnetwork_job(subnet["metadata"]["name"], ip, "auto")
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    client.delete(subnet)


def test_job_mac():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    cidr = "192.168.78.0/24"
    subnet = create_flatnetwork_subnet(client, cidr)

    # validate mac syntax
    try:
        mac = "888888:1a:ff:e5:d8:05"
        check = create_flatnetwork_job(subnet["metadata"]["name"], "auto", mac)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate single fixed mac and multiple ips
    try:
        mac = get_random_macs(1)[0]
        ips = "-".join(get_random_ips_from_cidr(subnet["spec"]["cidr"], 2))
        check = create_flatnetwork_job(subnet["metadata"]["name"], ips, mac)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate multiple fixed ips and macs
    try:
        macs = "-".join(get_random_macs(3))
        ips = "-".join(get_random_ips_from_cidr(subnet["spec"]["cidr"], 2))
        check = create_flatnetwork_job(subnet["metadata"]["name"], ips, mac)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate duplicate macs
    try:
        macs = "82:1a:ff:e5:d8:05-82:1a:ff:e5:d8:05"
        check = create_flatnetwork_job(subnet["metadata"]["name"], ips, mac)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    # validate used macs
    try:
        mac = get_random_macs(1)[0]
        pod = create_flatnetwork_pod(client, ns, "test-job-mac", BUSYBOX_IMAGE, "auto", mac,
                                 subnet["metadata"]["name"])
        assert pod is not None
        time.sleep(3)
        check = create_flatnetwork_job(subnet["metadata"]["name"], ips, mac)
        assert check is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    client.delete(subnet)


def test_ip_conflict_in_subnet():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]

    vlan = 1024
    cidr = "192.168.79.0/24"
    ranges_a = [
        {
            "from": "192.168.79.10",
            "to": "192.168.79.30"
        },
        {
            "from": "192.168.79.60",
            "to": "192.168.79.80"
        }
    ]
    subnet = create_flatnetwork_subnet(client, cidr, ranges=ranges_a, vlan=vlan)
    time.sleep(0.5)
    ranges_b = [
        {
            "from": "192.168.79.20",
            "to": "192.168.79.70"
        }
    ]
    try:
        subnet_b = create_flatnetwork_subnet(client, cidr, ranges=ranges_b, vlan=vlan)
        assert subnet_b is None
    except ApiError as e:
        assert e.error.status == 400
        assert "denied the request" in e.error.message

    client.delete(subnet)

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
