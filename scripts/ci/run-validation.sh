#!/bin/bash

# Run validation tests on GHA

set -euo pipefail

cd $(dirname $0)/../../

echo "Run validation tests"
echo "Current dir: $(pwd)"
./tests/validation/scripts/test-validation.sh | ./checker wrapper

echo "Validation test: DONE"
