# Validation Tests

Test scripts for rancher-flat-network (V2) & rancher-macvlan (V1) validation tests.

## Usage

1. Ensure Python 3.11 installed. 
1. Install dependencies.

    ```console
    $ cd tests/validation/
    $ pip install -r ./requirements.txt
    ```

1. Passing environment variables.

    ```sh
    export RANCHER_CLUSTER_NAME=local
    export CATTLE_TEST_URL='https://RANCHER_URL:30443'
    export RANCHER_TEST_SUBNET_MASTER='<MASTER_IFACE>'
    export ADMIN_TOKEN='<RANCHER_API_KEY>'
    ```

1. Run validation tests.

    ```sh
    pytest -n 3 -v -s testcase/<TESTCASE>/
    ```
