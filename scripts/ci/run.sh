#!/bin/bash

# Run provisioning tests on GHA

set -euo pipefail

cd $(dirname $0)/../../

cd ${TEST_SOURCE}/tests/provisioning/
echo Run test case: $TEST_CASE
echo "Current dir: $(pwd)"

./scripts/test-provisioning

echo Provisioning test: DONE
