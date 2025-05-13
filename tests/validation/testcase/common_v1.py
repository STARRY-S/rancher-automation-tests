from .common import *  # NOQA
import pprint
import json
import yaml
import rancher
import semver
import datetime


CATTLE_V1_API_URL = CATTLE_TEST_URL + "/v1"

TEST_IMAGE_V1 = os.environ.get('RANCHER_TEST_IMAGE_V1', "ranchertest/mytestcontainer")
headers = {"cookie": "R_SESS=" + ADMIN_TOKEN}

def get_admin_client_v1():
    url = CATTLE_V1_API_URL
    # in fact, we get the cluster client for the local cluster
    return rancher.Client(url=url, token=ADMIN_TOKEN, verify=False)


def get_cluster_client_for_token_v1(cluster_id=None, token=None):
    cluster = {}
    if cluster_id is None:
        cluster = get_cluster_by_name(get_admin_client_v1(), CLUSTER_NAME)
        cluster_id = cluster["id"]
    if token is None:
        token = ADMIN_TOKEN

    url = CATTLE_TEST_URL + "/k8s/clusters/" + cluster_id + "/v1/schemas"
    return rancher.Client(url=url, token=token, verify=False), cluster


def get_cluster_by_name(client, cluster_name):
    res = client.list_management_cattle_io_cluster()
    assert "data" in res.keys(), "failed to find any cluster in the setup"
    for cluster in res["data"]:
        if cluster["spec"]["displayName"] == cluster_name:
            return cluster
    assert False, "failed to find the cluster {}".format(cluster_name)


def get_project_by_name(client, cluster_id, project_name):
    res = client.list_management_cattle_io_project()
    assert "data" in res.keys(), "failed to find any project in the setup"
    for project in res["data"]:
        if project["spec"]["displayName"] == project_name \
                and project["spec"]["clusterName"] == cluster_id:
            return project
    assert False, "failed to find the project {} in cluster {}".format(project_name, cluster_id)


def create_ns_v1(cluster_id, project, ns_name):
    url = CATTLE_TEST_URL + "/k8s/clusters/" + cluster_id + "/v1/namespaces"
    ns = {
            "type": "namespace",
            "metadata": {
                "annotations": {
                    "field.cattle.io/containerDefaultResourceLimit": "{}",
                    "field.cattle.io/projectId": project.id
                },
                "labels": {
                    "field.cattle.io/projectId": project.id.split(":")[0]
                },
                "name": ns_name
            },
            "disableOpenApiValidation": False
        }
    r = requests.post(url, json=ns, verify=False, headers=headers)
    assert r.status_code == 201
    return r.json()


def delete_ns_v1(cluster_id, ns_name):
    url = CATTLE_TEST_URL + "/k8s/clusters/" + cluster_id + "/v1/namespaces/" + ns_name
    r = requests.delete(url, verify=False, headers=headers)
    assert r.status_code == 200


def display(res):
    if res is None:
        print("None object is returned")
        return
    if isinstance(res, dict) and "data" in res.keys():
        print("count of data {}".format(len(res.data)))
        for item in res.get("data"):
            print("-------")
            pprint.pprint(item)
        return
    else:
        print("This is a instance of {}".format(type(res)))
        pprint.pprint(res)


def read_json_from_resource_dir(dir, filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        with open('{}/../resource/{}/{}'.format(dir_path, dir, filename)) as f:
            data = json.load(f)
        return data
    except FileNotFoundError as e:
        assert False, e


def read_yaml_from_resource_dir(dir, filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        with open('{}/../resource/{}/{}'.format(dir_path, dir, filename)) as f:
            data = yaml.safe_load(f)
        return data
    except FileNotFoundError as e:
        assert False, e


def get_chart_latest_version(client, catalog, chart_name):
    # Refrest pandaria-catalog repo
    now = datetime.datetime.now(datetime.timezone.utc)
    catalog.spec.forceUpdate = now.strftime("%Y-%m-%dT%H:%M:%SZ") # 2025-05-13T07:05:19Z"
    client.update(catalog, catalog)
    print("Refreshing pandaria-catalog repository")
    time.sleep(15)

    # Fetch the latest chart version
    headers = {"Accept": "application/json",
               "Authorization": "Bearer " + ADMIN_TOKEN}
    url = catalog["links"]["index"]
    response = requests.get(url=url, verify=False, headers=headers)
    assert response.status_code == 200, \
        "failed to get the response from {}".format(url)
    assert response.content is not None, \
        "no chart is returned from {}".format(url)
    res = json.loads(response.content)
    assert chart_name in res["entries"].keys(), \
        "failed to find the chart {} from the chart repo".format(chart_name)
    charts = res['entries'][chart_name]
    versions = []
    for chart in charts:
        versions.append(chart["version"])
    latest = versions[0]
    for version in versions:
        if semver.compare(latest, version) < 0:
            latest = version
    return latest
