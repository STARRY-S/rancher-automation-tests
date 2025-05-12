#!/bin/bash

set -euo pipefail
cd $(dirname $0)

source utils.sh

echo "Install autoK3s"
sudo bash -c "curl -sLf https://github.com/cnrancher/autok3s/releases/download/${AUTOK3S_VERSION}/autok3s_linux_amd64 > /usr/bin/autok3s"
sudo chmod +x /usr/bin/autok3s
sudo mkdir -p /opt/config/autok3s
sudo chmod 777 /opt/config/autok3s

# Prepare registries.yaml & userdata script to /tmp
prepare_environment;

# Get autoK3s Provider Args
get_provider_args;

# Create Rancher Prime local cluster server
autok3s create --provider ${AUTOK3S_PROVIDER} \
    --name ${RPM_LOCAL_NAME} \
    --master 1 \
    --k3s-version ${K3S_VERSION} \
    --ssh-user ${AUTOK3S_SSH_USER} \
    --ssh-key-path /opt/config/autok3s/${SSH_KEY_NAME} \
    --registry /tmp/registries.yaml \
    ${AUTOK3S_CREATE_ARGS:-} &> autok3s_log.txt

echo "--------------------------------------"
echo "Wait 90 seconds for K3s server Ready..."
sleep 90

wait_rpm_server_ready;

get_rpm_config;

# Export env
echo "RANCHER_SERVER_URL=$RANCHER_SERVER_URL" >> $GITHUB_ENV
echo "RANCHER_SERVER_TOKEN=$RANCHER_SERVER_TOKEN" >> $GITHUB_ENV

echo "::add-mask::$RANCHER_SERVER_URL"
echo "::add-mask::$RANCHER_SERVER_TOKEN"

echo "rancher-server: Done"
