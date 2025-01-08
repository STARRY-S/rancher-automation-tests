#!/bin/bash

set -euo pipefail

cd $(dirname $0)

export RANCHER_CLUSTER_NAME=${RANCHER_CLUSTER_NAME:-local}
export CATTLE_TEST_URL="https://$RANCHER_SERVER_URL"
export RANCHER_TEST_SUBNET_MASTER="${RANCHER_TEST_SUBNET_MASTER:-ens5}"
export ADMIN_TOKEN="${RANCHER_SERVER_TOKEN}"

echo "Start run validation tests."

failed=""
for CASE in ${TEST_CASE[@]}; do
    echo "Running validation test case ${CASE}"
    ./${CASE} || {
        failed=1
        true
    }
done

if [[ ! -z "$failed" ]]; then
    echo "Some tests failed." >&2
fi

echo "validation test: Done"
