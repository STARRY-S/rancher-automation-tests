import pytest

from .common import *  # NOQA

subnet_cidr = "192.168.16.0/24"


def test_auto():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    job = create_flatnetwork_job(subnet["metadata"]["name"],
                             "auto",
                             "auto")

    busybox_pods = get_flatnetwork_job_pods(job)
    assert len(busybox_pods) == 1

    wait_for_job(job)
    pod_ip = get_flatnetwork_pod_ip(busybox_pods[0])
    assert ip_in_subnet(pod_ip, subnet["spec"]["cidr"])

    client.delete(job)


def test_fixed_ip():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    expected_ip = get_random_ips_from_cidr(subnet["spec"]["cidr"], 1)[0]
    job = create_flatnetwork_job(subnet["metadata"]["name"],
                             expected_ip,
                             "auto")

    busybox_pods = get_flatnetwork_job_pods(job)
    assert len(busybox_pods) == 1

    wait_for_job(job)
    pod_ip = get_flatnetwork_pod_ip(busybox_pods[0])
    assert pod_ip == expected_ip

    client.delete(job)


def test_fixed_mac():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    expected_mac = get_random_macs(1)[0]
    job = create_flatnetwork_job(subnet["metadata"]["name"],
                             "auto",
                             expected_mac)

    busybox_pods = get_flatnetwork_job_pods(job)
    assert len(busybox_pods) == 1

    wait_for_job(job)
    pod_mac = get_flatnetwork_pod_mac(busybox_pods[0])
    assert pod_mac == expected_mac

    client.delete(job)


def test_single_nic():
    client = factory["client"]
    cluster = factory["cluster"]
    ns = factory["ns"]
    subnet = factory["subnet"]

    job = create_flatnetwork_job(subnet["metadata"]["name"],
                             "auto",
                             "auto",
                             mode="single")

    busybox_pods = get_flatnetwork_job_pods(job)
    assert len(busybox_pods) == 1

    wait_for_job(job)
    pod_ip = get_flatnetwork_pod_ip(busybox_pods[0], nic="eth0")
    assert ip_in_subnet(pod_ip, subnet["spec"]["cidr"])

    client.delete(job)


def get_flatnetwork_job_pods(job):
    client = factory["client"]

    label_key = "job-name"
    label_value = job["metadata"]["name"]
    pods = client.list_pod(labelSelector=f'{label_key}={label_value}').data
    return pods


def create_flatnetwork_job(subnet, ip, mac, mode="dual", skip_wait=False):
    client = factory["client"]
    ns_name = factory['ns']["metadata"]["name"]
    name = random_test_name("busybox")
    template = read_json_from_resource_dir("flatnetwork", "job.json")
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

    template["spec"] = spec

    job = client.create_batch_job(template)
    if not skip_wait:
        wait_for(lambda: client.reload(job).metadata.state.name == "active",
                 timeout_message="time out waiting for job to be ready")
    return client.reload(job)


def wait_for_job(job):
    client = factory["client"]

    time.sleep(3)

    wait_for(lambda: ("ready" in client.reload(job).status and \
                      client.reload(job).status.ready == 1) or \
                     ("active" in client.reload(job).status and \
                      client.reload(job).status.active == 1),
             timeout_message="time out waiting for job to be ready")


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
    factory["subnet"] = create_flatnetwork_subnet(
        factory["client"],
        subnet_cidr,
        vlan=vlan)

    def fin():
        client = factory["client"]
        cluster = factory['cluster']
        ns = factory['ns']
        delete_ns_v1(cluster.id, ns["metadata"]["name"])
        client.delete(factory["project"])
        client.delete(factory["subnet"])
    request.addfinalizer(fin)
