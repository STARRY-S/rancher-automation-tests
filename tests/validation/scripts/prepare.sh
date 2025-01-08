#!/bin/bash

set -exuo pipefail

cd $(dirname $0)/../

KUBECTL_VERSION=${KUBECTL_VERSION:-v1.32.0}
HELM_VERSION=${HELM_VERSION:-v3.16.4}

echo "Install helm"
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | sudo bash -s -- --version $HELM_VERSION
ln -s /usr/local/bin/helm /usr/local/bin/helm_v3

echo "Install kubectl"
curl -LO "https://dl.k8s.io/release/$KUBECTL_VERSION/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/kubectl

sudo apt-get update
sudo apt-get install -y \
    libsasl2-dev libldap2-dev libssl-dev gcc libpq-dev python3-dev python3-pip python3-venv python3-wheel

echo "Install pip dependencies"
pip install -r requirements.txt

echo "preapre: Done"
