import pytest

from .common import *  # NOQA


m_chart_name = 'rancher-macvlan'
m_version = os.environ.get('RANCHER_MACVLAN_VERSION', None)
m_app = 'kube-system/rancher-macvlan'
m_namespace = "kube-system"


def test_install_macvlan():
    client = factory['client']

    if client.by_id_apps_deployment(id="kube-system/network-controller") is not None:
        pytest.skip("APP has been installed")

    app = client.by_id_catalog_cattle_io_app(m_app)
    if app is not None:
        pytest.skip("APP has been installed")

    install_macvlan()


def install_macvlan():
    client = factory['client']
    pandaria_catalog = factory['pandaria_catalog']

    global m_version
    if m_version is None:
        m_version = get_chart_latest_version(client, pandaria_catalog, m_chart_name)
        print(f"chart version is not provided, get chart version from repo: {m_version}")

    cluster_id = factory["cluster"]["id"]
    cluster_name = factory["cluster"]["spec"]["displayName"]
    values = read_json_from_resource_dir("macvlan", "rancher_macvlan_values.json")
    for chart in values["charts"]:
        chart["version"] = m_version
        chart["values"]["global"]["cattle"]["clusterId"] = cluster_id
        chart["values"]["global"]["cattle"]["clusterName"] = cluster_name
        chart["values"]["global"]["cattle"]["url"] = CATTLE_TEST_URL
        chart["values"]["clusterType"] = "K3s"
        chart["values"]["multus"]["cniVersion"] = "1.0.0"
    print(values)
    client.action(pandaria_catalog, "install", values)
    # wait 1 minutes for the app to be fully deployed
    time.sleep(60)
    # check the app
    wait_for(
        lambda: client.by_id_catalog_cattle_io_app(m_app).status.summary.state == "deployed",
        timeout_message="time out waiting for app to be ready")
