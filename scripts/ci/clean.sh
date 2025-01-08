#!/bin/bash

cd $(dirname $0)/../../

set -exuo pipefail

rm -rf ${RANCHER_SOURCE:-"UNKNOW"} || true
rm /opt/config/autok3s/${SSH_KEY:-} || true
rm -r ${HOME}/.ssh/ || true

# Build checker cli
./scripts/build.sh

CLOUD=${1:-hwcloud}

echo "Wait a few seconds to cleanup remaining resources..."
sleep 10
echo "Start cleanup cloud resources: $CLOUD"

./checker $CLOUD \
    --filter="auto-rancher-" \
    --filter="oetest" \
    --filter="auto-aws-" \
    --output="remain-resources.txt" \
    --auto-yes \
    --clean

if [[ -e "remain-resources.txt" ]]; then
    echo "Cleaning up $CLOUD resources:"
    cat remain-resources.txt
    rm remain-resources.txt
    echo
    echo "Waiting for resources cleanup..."
    sleep 60
    ./checker $CLOUD \
        --filter="auto-rancher-" \
        --filter="oetest-" \
        --filter="auto-aws-" \
        --output="remain-resources.txt" \
        --auto-yes \

    if [[ -e "remain-resources.txt" ]]; then
        echo "There still have some remaining resources:"
        cat remain-resources.txt
        echo
        echo "Please check manually!"
        exit 1
    fi
fi

echo "Cleanup: DONE"
