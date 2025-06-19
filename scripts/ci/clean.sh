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
sleep 30
echo "Start cleanup cloud resources: $CLOUD"

CHECK_OPTIONS=""
case ${CLOUD} in
    aws)
        CHECK_OPTIONS="${CHECK_OPTIONS} --check-eks=false"
        ;;
    hwcloud)
        CHECK_OPTIONS="${CHECK_OPTIONS}"
        ;;
    tencent)
        CHECK_OPTIONS="${CHECK_OPTIONS}"
        ;;
esac

./checker $CLOUD \
    --filter="auto-rancher-" \
    --filter="oetest" \
    --filter="auto-aws-" \
    --exclude="DoNotDelete" \
    --output="remain-resources.txt" \
    ${CHECK_OPTIONS} \
    --auto-yes \
    --clean

if [[ -e "remain-resources.txt" ]]; then
    echo "Cleaning up $CLOUD resources:"
    cat remain-resources.txt
    rm remain-resources.txt
    echo
    echo "Waiting for resources cleanup..."
    sleep 180
    ./checker $CLOUD \
        --filter="auto-rancher-" \
        --filter="oetest-" \
        --filter="auto-aws-" \
        --exclude="DoNotDelete" \
        --output="remain-resources.txt" \
        ${CHECK_OPTIONS} \
        --auto-yes

    if [[ -e "remain-resources.txt" ]]; then
        echo "There still have some remaining resources:"
        cat remain-resources.txt
        echo
        echo "Please check manually!"
        exit 1
    fi
fi

echo "Cleanup: DONE"
