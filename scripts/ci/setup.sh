#!/bin/bash

# Setup test environment on GHA

set -euo pipefail

cd $(dirname $0)/../../

RANCHER_SOURCE="$HOME/rancher"
RANCHER_REPO="https://${RANCHER_REPO_OAUTH_TOKEN}@${RANCHER_CODE_REPO}"

# Setup INPUT_ENVS
array=($INPUT_ENVS)
for i in "${array[@]}"
do
    echo $i >> "$GITHUB_ENV"
    echo "Export ENV [$i] from workflow inputs"
done

echo "RANCHER_SOURCE=${RANCHER_SOURCE}" >> $GITHUB_ENV

# Install dependencies
echo "CATTLE_MACHINE_VERSION: $CATTLE_MACHINE_VERSION"
sudo apt install -y tar gzip jq gawk
sudo bash -c "curl -sLf https://github.com/rancher/machine/releases/download/${CATTLE_MACHINE_VERSION}/rancher-machine-amd64.tar.gz | tar xvzf - -C /usr/bin"

# Clone Rancher source code
IFS='.' read -r -a array <<< $RPM_VERSION
echo "Clone Rancher source code..."
RANCHER_BRANCH="release/${array[0]}.${array[1]}-ent"
echo "Rancher branch: ${RANCHER_BRANCH}"
git clone --depth=1 --single-branch --branch ${RANCHER_BRANCH} $RANCHER_REPO $RANCHER_SOURCE

# Prepare ssh private key
cp /opt/config/autok3s/$SSH_KEY tests/provisioning/$SSH_KEY

# Pre-download Rancher go mod dependencies
echo "Pre-download rancher go mod dependencies"
cd $RANCHER_SOURCE
# go mod tidy

# Install gotestsum
echo "Install gotestsum"
go install gotest.tools/gotestsum@latest

# Prepare base config file
cat > ${RANCHER_SOURCE}/tests/v2/validation/provisioning/config_panda_base << EOT
rancher:
  host: "$RANCHER_SERVER_URL"
  adminToken: "$RANCHER_SERVER_TOKEN"
  cleanup: false
  insecure: true
EOT

echo "Setup: DONE"
