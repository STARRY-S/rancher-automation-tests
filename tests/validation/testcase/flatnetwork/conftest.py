import pytest

from .common import *  # NOQA


@pytest.fixture(scope='package', autouse="True")
def setup_package(request):
    # intialize v1 client
    v3_admin_client = get_admin_client()
    c_client, cluster = get_cluster_client_for_token_v1()
    create_kubeconfig(cluster)
    factory["client"] = c_client
    factory["v3_admin_client"] = v3_admin_client
    factory["cluster"] = cluster
    pandaria_catalog = \
        c_client.by_id_catalog_cattle_io_clusterrepo(id="pandaria-catalog")
    if pandaria_catalog is None:
        assert False, "pandaria_catalog is not available"
    factory["pandaria_catalog"] = pandaria_catalog

    factory["worker_nodes"] = get_worker_nodes(c_client)
