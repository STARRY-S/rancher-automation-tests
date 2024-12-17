#!/bin/bash

cd $(dirname $0)/../../

set -exuo pipefail

rm ${TEST_SOURCE}/tests/provisioning/$SSH_KEY || true
rm /opt/config/autok3s/$SSH_KEY || true
rm -r ${HOME}/.ssh/ || true
rm -rf ${RANCHER_SOURCE} || true
rm -rf ${TEST_SOURCE} || true
