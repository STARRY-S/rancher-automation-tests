#!/bin/bash

set -euo pipefail

cd $(dirname $0)/../

cd src/tests/provisioning/

echo Run test case: $TEST_CASE

make test-provisioning

echo DONE
