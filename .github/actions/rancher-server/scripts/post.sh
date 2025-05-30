#!/bin/bash

set -euo pipefail
cd $(dirname $0)

rm -rf /opt/config/autok3s/ || true
rm -r ${HOME}/.ssh/ || true

if ! command -v autok3s &> /dev/null; then
    exit 0
fi

echo "Cleanup cluster: $RPM_LOCAL_NAME"
autok3s delete -p ${AUTOK3S_PROVIDER} -n ${RPM_LOCAL_NAME} -f
echo "--------------------------"

if [[ -e autok3s_log.txt ]]; then
    echo "autok3s create log:"
    cat autok3s_log.txt
    echo "--------------------------"
fi

echo "post: Done"
