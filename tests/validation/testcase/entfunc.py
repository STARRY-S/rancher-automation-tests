from .common import *  # NOQA
from time import gmtime
from netaddr import *
import yaml


DEFAULT_NODEPOOL_TIMEOUT = 300
TEST_INTERNAL_IMAGE = os.environ.get('RANCHER_TEST_IMAGE', "busybox:musl")
TEST_INGRESS_TARGET_PORT = os.environ.get('RANCHER_TEST_INGRESS_TARGET_PORT', "8088")

def get_admin_client_byToken(url, token):
    return rancher.Client(url=url, token=token, verify=False)


def validate_service(ns, service):
    '''
    desc: check service exist
    :param ns: namespace
    :param service: service name
    :return: 0 exist ; 1 not exist
    '''
    service_cmd = "get service -n " + ns + " " + service
    result = execute_kubectl_cmd_with_code(service_cmd, json_out=False, stderr=False, stderrcode=True)
    return result


def get_events(ns_name,object_name,object_kind):
    cmd = "get events -n " + ns_name + " --field-selector=involvedObject.name=" + object_name \
          + ",involvedObject.kind=" + object_kind
    exec_result=execute_kubectl_cmd(cmd, json_out=True)
    return exec_result


def get_kubectl_exec_code(pod, ns, cmd):
    exec_cmd = "exec " + pod + " -n " + ns + " -- " + cmd
    result = execute_kubectl_cmd_with_code(exec_cmd, json_out=False, stderr=False, stderrcode=True)
    return result


def get_kubectl_exec_output(pod, ns, cmd):
    exec_cmd = "exec " + pod + " -n " + ns + " -- " + cmd
    result = execute_kubectl_cmd_with_code(exec_cmd, json_out=False, stderr=False, stderrcode=False)
    return result


def validate_wl_byName(p_client, wl_name, ns_name, type, wait_for_cron_pods=60):
    wl = p_client.list_workload(name=wl_name).data
    assert len(wl) == 1
    wl = wl[0]
    workload = wait_for_wl_to_active(p_client, wl)
    assert workload.state == "active"
    if type == "cronJob":
        time.sleep(wait_for_cron_pods)
    pods = p_client.list_pod(workloadId=workload.id).data
    pod_count = len(pods)
    assert pod_count > 0
    for pod in pods:
        wait_for_pod_to_running(p_client, pod)
    wl_result = execute_kubectl_cmd(
        "get " + type + " " + workload.name + " -n " + ns_name)
    if type == "deployment" or type == "statefulSet":
        assert wl_result["status"]["readyReplicas"] == pod_count
    if type == "daemonSet":
        assert wl_result["status"]["currentNumberScheduled"] == pod_count
    if type == "cronJob":
        assert len(wl_result["status"]["active"]) >= pod_count
        return
    label = ""
    for key, value in workload.workloadLabels.items():
        label = label + key + "=" + value + ","
    get_pods = "get pods -l" + label[:-1] + " -n " + ns_name
    pods_result = execute_kubectl_cmd(get_pods)
    assert len(pods_result["items"]) == pod_count
    for pod in pods_result["items"]:
        assert pod["status"]["phase"] == "Running"
    return pods_result["items"]


def get_admin_client_and_cluster_byUrlToken(url, token):
    client = get_admin_client_byToken(url, token)
    if CLUSTER_NAME == "":
        clusters = client.list_cluster().data
    else:
        clusters = client.list_cluster(name=CLUSTER_NAME).data
    assert len(clusters) > 0
    cluster = clusters[0]
    return client, cluster

def wait_for_wl_delete(client, workload, timeout=DEFAULT_TIMEOUT):
    workloads = client.list_workload(name=workload).data
    start = time.time()
    while len(workloads) != 0:
        if time.time() - start > timeout:
            raise AssertionError(
                "Timed out waiting for state to get to active")
        time.sleep(.5)
        workloads = client.list_workload(name=workload).data
    return workloads


def wait_for_pod_delete(client, workload, timeout=DEFAULT_TIMEOUT):
    pods = client.list_pod(workloadId=workload.id).data
    start = time.time()
    while len(pods) != 0:
        if time.time() - start > timeout:
            raise AssertionError(
                "Timed out waiting for state to get to active")
        time.sleep(.5)
        pods = client.list_pod(workloadId=workload.id).data
    return pods

def wait_for_project_delete(client, cluster, project, timeout=DEFAULT_TIMEOUT):
    projects = client.list_project(name=project,clusterId=cluster.id).data
    start = time.time()
    while len(projects) != 0:
        if time.time() - start > timeout:
            raise AssertionError(
                "Timed out waiting for state to get to active")
        time.sleep(.5)
        projects = client.list_project(name=project, clusterId=cluster.id).data
    return projects

# ------ tools ------
def split_to_list(str):
    # des : split wl network ip/mac
    if str == "auto":
        return str
    return str.split("-")

def validate_in_list(str,list):
    # des : remove pod exist ip/mac
    assert str in list
    list.remove(str)
    return list

def exchange_mask(mask):
    count_bit = lambda bin_str: len([i for i in bin_str if i=='1'])
    mask_splited = mask.split(".")
    mask_count = [count_bit(bin((int(i)))) for i in mask_splited]
    return sum(mask_count)

def exchange_maskint(mask_int):
    bin_arr = ['0' for i in range(32)]
    for i in range(mask_int):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)

# ------ run cmd ------
def execute_kubectl_cmd_with_code(cmd, json_out=True, stderr=False, stderrcode=False):
    command = 'kubectl --kubeconfig {0} {1}'.format(
        kube_fname, cmd)
    result = ""
    if json_out:
        command += ' -o json'
    if stderr:
        result = run_command_with_stderr(command)
    if stderrcode:
        result = run_command_with_stderr_code(command)
    else:
        result = run_command(command)
    if json_out:
        result = json.loads(result)
    return result

def run_command_with_stderr_code(command):
    try:
        output = subprocess.check_output(command, shell=True,
                                         stderr=subprocess.PIPE)
        returncode = 0
    except subprocess.CalledProcessError as e:
        output = e.output
        returncode = e.returncode
    return returncode

def execute_kubectl_cmd_with_stderr_output(cmd):
    command = 'kubectl --kubeconfig {0} {1}'.format(
        kube_fname, cmd)
    result = run_command_error_with_stderr(command)
    return result


def run_command_error_with_stderr(command):
    try:
        output = subprocess.check_output(command, shell=True,
                                         stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        output = e.stderr
    return output

def create_general_user(client, username, password):
    user = {
        "enabled": True,
        "mustChangePassword": False,
        "type": "user",
        "username": username,
        "password": password
    }
    generalUser = client.create_user(user)
    globalrolebinding = {
        "type": "globalRoleBinding",
        "globalRoleId": "user",
        "userId": generalUser.id
    }
    client.create_globalRoleBinding(globalrolebinding)
    return generalUser

def delete_general_user(user):
    reUrl = CATTLE_TEST_URL + "/v3" + "/users/" + user.id
    headers = {'Authorization': 'Bearer ' + ADMIN_TOKEN}
    re = requests.delete(reUrl, headers=headers, verify=False)
    assert re.status_code == 200, "delete general user failed"

def get_auth_token(username, password, reUrl):
    headers = {'Authorization': 'Bearer '}
    var = {
        "username": username,
        "password": password,
        "description": "UI Session",
        "ttl": 57600000,
        "labels": {
            "ui-session": "true"
        }
    }
    re = requests.post(reUrl, json=var, verify=False, headers=headers)
    assert re.status_code == 201
    return re.json()['token']
