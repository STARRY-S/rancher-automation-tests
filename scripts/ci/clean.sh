#!/bin/bash

cd $(dirname $0)/../../

set -exuo pipefail

rm -rf $RANCHER_SOURCE || true
rm /opt/config/autok3s/$SSH_KEY || true
rm -r ${HOME}/.ssh/ || true

# Build checker cli
./scripts/build.sh

CLOUD=${1:-hwcloud}

sleep 5
echo "Start cleanup cloud resources: $CLOUD"
set -x
./checker $CLOUD --filter="auto-rancher-" --clean
