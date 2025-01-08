## FlatNetwork V2 validation testcase

## Environments

```sh
export RANCHER_CLUSTER_NAME=local
export CATTLE_TEST_URL='https://RANCHER_URL:30443'
export RANCHER_TEST_SUBNET_MASTER='<MASTER_IFACE>'
export ADMIN_TOKEN='<RANCHER_API_KEY>'
```

## Run Tests

```sh
pytest -n 3 -v -s testcase/macvlan/
```
