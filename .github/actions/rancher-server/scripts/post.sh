#!/bin/bash

set -euo pipefail
cd $(dirname $0)

rm -rf /opt/config/autok3s/ || true
rm -r ${HOME}/.ssh/ || true

if ! command -v autok3s &> /dev/null; then
    exit 0
fi

if [[ -e autok3s_log.txt ]]; then
    echo "autok3s create log:"
    cat autok3s_log.txt
    echo "--------------------------"
fi

echo "Cleanup cluster: $RPM_LOCAL_NAME"
PROVIDER=$AUTOK3S_PROVIDER
if [[ $PROVIDER = awscn ]]; then
    PROVIDER=aws
fi
autok3s delete -p ${PROVIDER} -n ${RPM_LOCAL_NAME} -f

echo "post: Done"
