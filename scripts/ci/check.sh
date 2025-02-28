#!/bin/bash

# Check public cloud remaining resources

cd $(dirname $0)/../../

set -euo pipefail

# Build checker cli
./scripts/build.sh

CLOUDS=(
    "aws"
    "awscn"
    "hwcloud"
    "tencent"
    # "aliyun" # TODO: add aliyun support
)

for CLOUD in ${CLOUDS[@]}; do
    PROVIDER=$CLOUD
    if [[ $CLOUD = "aws" ]]; then
        export AWS_AK="$AWS_AK"
        export AWS_SK="$AWS_SK"
        export AWS_REGION="$AWS_REGION"
    elif [[ $CLOUD = "awscn" ]]; then
        export AWS_AK="$AWSCN_AK"
        export AWS_SK="$AWSCN_SK"
        export AWS_REGION="$AWSCN_REGION"
        PROVIDER="aws"
    fi

    echo "Checking resources of cloud [$CLOUD]"
    ./checker $PROVIDER \
        --filter="auto-rancher-" \
        --filter="oetest" \
        --filter="auto-aws-" \
        --filter="starry" \
        --filter="eip" \
        --filter="rancher" \
        --output="remain-resources.txt" \
        --auto-yes

    if [[ -e "remain-resources.txt" ]]; then
        echo "-----------------------------"
        echo "$CLOUD resources:"
        cat remain-resources.txt
        echo
        echo "There are unstopped resources on $CLOUD" >&2
        echo "Please check manually!" >&2
        echo
        echo "CHECK: FAILED" >&2
        exit 1
    fi
done

echo "CHECK: PASS"
