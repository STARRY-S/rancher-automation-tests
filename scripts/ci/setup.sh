#!/bin/bash

# Setup test environment on GHA

set -euo pipefail

cd $(dirname $0)/../../

TEST_SOURCE="$HOME/pandaria-tests"
TEST_REPO="https://${TEST_REPO_OAUTH_TOKEN}@${TEST_CODE_REPO}"

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
echo "TEST_SOURCE=${TEST_SOURCE}" >> $GITHUB_ENV

# Install dependencies
echo "CATTLE_MACHINE_VERSION: $CATTLE_MACHINE_VERSION"
sudo apt install -y tar gzip jq gawk
sudo bash -c "curl -sLf https://github.com/rancher/machine/releases/download/${CATTLE_MACHINE_VERSION}/rancher-machine-amd64.tar.gz | tar xvzf - -C /usr/bin"
sudo bash -c "curl -sLf https://github.com/cnrancher/autok3s/releases/download/${AUTOK3S_VERSION}/autok3s_linux_amd64 > /usr/bin/autok3s  && chmod +x /usr/bin/autok3s"
sudo mkdir -p /opt/config/autok3s
sudo chmod 777 /opt/config/autok3s

# Clone Rancher source code
IFS='.' read -r -a array <<< $RPM_VERSION
echo "Clone Rancher source code..."
RANCHER_BRANCH="release/${array[0]}.${array[1]}-ent"
echo "Rancher branch: ${RANCHER_BRANCH}"
git clone --depth=1 --single-branch --branch ${RANCHER_BRANCH} $RANCHER_REPO $RANCHER_SOURCE

# Clone test code scripts repo
echo "Clone Provisioning test source code..."
git clone --depth=1 --single-branch --branch ${TEST_CODE_BRANCH} $TEST_REPO $TEST_SOURCE

# Prepare ssh private key
touch ${TEST_SOURCE}/tests/provisioning/$SSH_KEY
cat > "${TEST_SOURCE}/tests/provisioning/$SSH_KEY" << EOT
$SSH_KEY_PAIR
EOT
chmod 600 ${TEST_SOURCE}/tests/provisioning/$SSH_KEY
cp ${TEST_SOURCE}/tests/provisioning/$SSH_KEY /opt/config/autok3s/$SSH_KEY

# Pre-download Rancher go mod dependencies
echo "Pre-download rancher go mod dependencies"
cd $RANCHER_SOURCE
go mod tidy

# Install gotestsum
echo "Install gotestsum"
go install gotest.tools/gotestsum@latest

echo "Setup: DONE"
