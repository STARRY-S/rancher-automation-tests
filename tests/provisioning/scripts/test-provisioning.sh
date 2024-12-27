#!/bin/bash

set -euo pipefail

cd $(dirname $0)

echo "Start run provisioning tests."

failed=""
for CASE in ${TEST_CASE[@]}; do
    echo "Running provisioning case ${CASE}"
    ./${CASE} || failed=1
done

if [[ ! -z "$failed" ]]; then
    echo "Some tests failed, please cleanup resources manually!" >&2
fi
