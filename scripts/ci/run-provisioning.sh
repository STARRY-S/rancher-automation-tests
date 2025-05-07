#!/bin/bash

# Run provisioning tests on GHA

set -euo pipefail

cd $(dirname $0)/../../

echo "Run test case: [$TEST_CASE]"
echo "Current dir: $(pwd)"
./tests/provisioning/scripts/test-provisioning.sh | ./checker wrapper

echo Provisioning test: DONE
