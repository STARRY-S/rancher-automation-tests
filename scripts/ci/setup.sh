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

# Clone hosted-providers-e2e
HOSTED_PROVIDERS_E2E_SOURCE="$HOME/hosted-providers-e2e"
echo "Clone hosted-providers-e2e source code..."
git clone --depth=1 --single-branch --branch main https://github.com/rancher/hosted-providers-e2e.git $HOSTED_PROVIDERS_E2E_SOURCE
# Prepare EKS e2e config file
cat > $HOSTED_PROVIDERS_E2E_SOURCE/cattle-config-provisioning.yaml << EOT
rancher:
  cleanup: false
  insecure: true
awsCredentials:
  accessKey: ""
  defaultRegion: cn-northwest-1
  secretKey: ""
eksClusterConfig:
  kmsKey: ""
  kubernetesVersion: "1.31"
  loggingTypes: []
  nodeGroups:
  - desiredSize: 1
    diskSize: 20
    ec2SshKey: ""
    gpu: false
    imageId: ""
    labels: {}
    maxSize: 1
    minSize: 1
    nodeRole: arn:aws-cn:iam::801570287679:role/starry-test-eks-node-role
    nodegroupName: test1
    requestSpotInstances: true
    resourceTags: {}
    spotInstanceTypes:
    - t3a.medium
    - t3.medium
    subnets:
    - subnet-0c512a880509158d2
    - subnet-02aab467ed72a912f
    - subnet-0ad3642defaf29191
    securityGroups:
    - sg-0190e73d5ec40f125
    serviceRole: eksClusterRole
    tags: {}
    userData: ""
    version: "1.31"
EOT
echo "HOSTED_PROVIDERS_E2E_SOURCE=${HOSTED_PROVIDERS_E2E_SOURCE}" >> $GITHUB_ENV

# Prepare ssh private key
cp /opt/config/autok3s/$SSH_KEY tests/provisioning/$SSH_KEY

# Pre-download Rancher go mod dependencies
echo "Pre-download rancher go mod dependencies"
cd $RANCHER_SOURCE
go mod tidy

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
