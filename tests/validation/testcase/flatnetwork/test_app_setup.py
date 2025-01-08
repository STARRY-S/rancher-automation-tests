import pytest

from .common import *  # NOQA


m_chart_name = 'rancher-flat-network'
m_version = os.environ.get('RANCHER_FLAT_NETWORK_VERSION', None)
m_app = 'cattle-flat-network/rancher-flat-network'
m_namespace = "cattle-flat-network"


def test_install_flatnetwork():
    client = factory['client']

    if client.by_id_apps_deployment(id="cattle-flat-network/rancher-flat-network-operator") is not None:
        pytest.skip("APP has been installed")

    app = client.by_id_catalog_cattle_io_app(m_app)
    if app is not None:
        pytest.skip("APP has been installed")

    install_flatnetwork()


def install_flatnetwork():
    client = factory['client']
    pandaria_catalog = factory['pandaria_catalog']

    global m_version
    if m_version is None:
        m_version = get_chart_latest_version(pandaria_catalog, m_chart_name)
        print(f"chart version is not provided, get chart version from repo: {m_version}")

    cluster_id = factory["cluster"]["id"]
    cluster_name = factory["cluster"]["spec"]["displayName"]
    values = read_json_from_resource_dir("flatnetwork", "chart_values.json")
    for chart in values["charts"]:
        chart["version"] = m_version
        chart["values"]["global"]["cattle"]["clusterId"] = cluster_id
        chart["values"]["global"]["cattle"]["clusterName"] = cluster_name
        chart["values"]["global"]["cattle"]["url"] = CATTLE_TEST_URL
        chart["values"]["clusterType"] = "K3s"
        if "multus" in chart["values"]:
            chart["values"]["multus"]["cni"]["version"] = "1.0.0"
    print(values)
    client.action(pandaria_catalog, "install", values)
    # wait 60 sec for the app to be fully deployed
    time.sleep(60)
    # check the app
    wait_for(
        lambda: client.by_id_catalog_cattle_io_app(m_app).status.summary.state == "deployed",
        timeout_message="timeout waiting for chart installed")
