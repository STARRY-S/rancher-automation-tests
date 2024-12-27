#!/bin/bash

cd $(dirname $0)/../../

set -exuo pipefail

rm /opt/config/autok3s/$SSH_KEY || true
rm -r ${HOME}/.ssh/ || true

# Build checker cli
./scripts/build.sh

echo "Check resource cleanup"
# Check cloud resource cleanup
./checker ${1:-"hwcloud"}
