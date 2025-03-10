#!/bin/bash

set -exuo pipefail

cd /tmp

ARCH="$(uname -m)"
while [[ ! -e "install-docker.sh" ]]; do
    wget --timeout=120 "https://starry-test.obs.cn-east-3.myhuaweicloud.com/docker/install-docker.sh" || true
    sleep 1
done
while [[ ! -e "containerd.tar.gz" ]]; do
    wget --timeout=120 "https://starry-test.obs.cn-east-3.myhuaweicloud.com/docker/${ARCH}/containerd.tar.gz" || true
    sleep 1
done
while [[ ! -e "docker.tar.gz" ]]; do
    wget --timeout=120 "https://starry-test.obs.cn-east-3.myhuaweicloud.com/docker/${ARCH}/docker.tar.gz" || true
    sleep 1
done

chmod +x install-docker.sh
mkdir -p /etc/docker
echo '{
    "registry-mirrors": [
        "https://registry.rancher.cn"
    ]
}' > /etc/docker/daemon.json

bash ./install-docker.sh

usermod -aG docker openeuler
