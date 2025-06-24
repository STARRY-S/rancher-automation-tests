#!/bin/bash

# UserData

set -euo pipefail
cd $(dirname $0)/../../

mkdir -p /var/lib/rancher/k3s/server/manifests

RPM_VERSION=$RPM_VERSION
ADMIN_PWD=$ADMIN_PWD
DOCKERHUB_USERNAME=$DOCKERHUB_USERNAME
IS_PSP_ENABLED=false
IS_POST_DELETE_ENABLED=false

RPM_REPO_BASE="https://charts.rancher.cn"
IFS='.' read -r -a array <<< $RPM_VERSION
RPM_REPO_BASE="${RPM_REPO_BASE}/${array[0]#v}.${array[1]}-prime"
if [[ "${RPM_VERSION}" == *"rc"* ]]; then
    RPM_REPO="${RPM_REPO_BASE}/dev"
else
    RPM_REPO="${RPM_REPO_BASE}/latest"
fi

SYSTEM_DEFAULT_REGISTRY=""
RANCHER_IMAGE="prime/rancher"
case $AUTOK3S_PROVIDER in
  aws)
    HOST_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    SYSTEM_DEFAULT_REGISTRY="registry.rancher.cn"
    RANCHER_IMAGE='registry.rancher.cn/prime/rancher'
    ;;
  awscn)
    HOST_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    SYSTEM_DEFAULT_REGISTRY="registry.rancher.cn"
    RANCHER_IMAGE='registry.rancher.cn/prime/rancher'
    ;;
  alibaba)
    HOST_IP=$(curl -s http://100.100.100.200/latest/meta-data/public-ipv4)
    SYSTEM_DEFAULT_REGISTRY="registry.rancher.cn"
    RANCHER_IMAGE="registry.rancher.cn/prime/rancher"
    ;;
  tencent)
    HOST_IP=$(curl -s http://metadata.tencentyun.com/latest/meta-data/public-ipv4)
    SYSTEM_DEFAULT_REGISTRY="registry.rancher.cn"
    RANCHER_IMAGE="registry.rancher.cn/prime/rancher"
    ;;
esac
echo "HOST_IP: ${HOST_IP}"
echo "SYSTEM_DEFAULT_REGISTRY: ${SYSTEM_DEFAULT_REGISTRY}"

cat > /var/lib/rancher/k3s/server/manifests/rancher.yaml << EOF
---
apiVersion: v1
kind: Namespace
metadata:
  name: cert-manager
---
apiVersion: v1
kind: Namespace
metadata:
  name: cattle-system
---
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  namespace: kube-system
  name: cert-manager
spec:
  targetNamespace: cert-manager
  version: v1.17.2
  chart: cert-manager
  repo: https://jetstack.hxstarrys.me
  set:
    installCRDs: "true"
---
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: rancher
  namespace: kube-system
spec:
  targetNamespace: cattle-system
  version: ${RPM_VERSION}
  chart: rancher
  repo: ${RPM_REPO}
  set:
    hostname: "$HOST_IP:30443"
    bootstrapPassword: "${ADMIN_PWD}"
    antiAffinity: "required"
    ingress.enabled: "false" # use nodeport
    replicas: 1
    global.cattle.psp.enabled: "${IS_PSP_ENABLED}"
    # postDelete.enabled: "${IS_POST_DELETE_ENABLED}" # disable post-delete hook instead of pulling post-delete image
    rancherImage: "${RANCHER_IMAGE}"
    systemDefaultRegistry: "${SYSTEM_DEFAULT_REGISTRY}"
    auditLog.destination: "hostPath"
    auditLog.maxAge: 7
    auditLog.level: 3
    useBundledSystemChart: "true"
    postDelete.image.repository: /rancher/shell
    extraEnv[0].name: "CATTLE_BASE_REGISTRY"
    extraEnv[0].value: ""
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: rancher
  name: rancher-lb-svc
  namespace: cattle-system
spec:
  ports:
    - name: http
      port: 30080
      protocol: TCP
      targetPort: 80
    - name: https
      port: 30443
      protocol: TCP
      targetPort: 443
  selector:
    app: rancher
  sessionAffinity: None
  type: LoadBalancer
EOF
