#!/bin/bash

# Run provisioning tests on GHA

set -euo pipefail

cd $(dirname $0)/../../

cd tests/provisioning/
echo "Run test case: [$TEST_CASE]"
echo "Current dir: $(pwd)"
./scripts/test-provisioning.sh

echo Provisioning test: DONE
