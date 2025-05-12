#!/bin/bash

# Run provisioning tests on GHA

set -euo pipefail

cd $(dirname $0)/../../

echo "Run awscn EKS e2e tests..."
echo "Current dir: $(pwd)"
./tests/provisioning/scripts/awscn/awscn-eks | ./checker wrapper

echo AWSCN EKS e2e test: DONE
