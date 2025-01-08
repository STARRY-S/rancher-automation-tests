#!/bin/bash

set -euo pipefail

get_provider_args() {
    echo "Create Rancher Prime Server by provider [$AUTOK3S_PROVIDER]"
    local AUTOK3S_CONTEXT=${AUTOK3S_REGION}.${AUTOK3S_PROVIDER}
    case ${AUTOK3S_PROVIDER} in
        aws)
            AUTOK3S_CREATE_ARGS="--keypair-name ${SSH_KEY_PAIR} --ami ${AUTOK3S_AMI} \
                --instance-type ${AUTOK3S_INSTANCE_TYPE} \
                --region ${AUTOK3S_REGION} --request-spot-instance \
                --root-size 50 --security-group ${AUTOK3S_SECURITY_GROUP} \
                --volume-type ${AUTOK3S_VOLUME_TYPE} \
                --vpc-id ${AUTOK3S_VPC} --zone ${AUTOK3S_ZONE} \
                --system-default-registry=docker.io \
                --user-data-path /tmp/userdata.sh"
            ;;
        awscn)
            AUTOK3S_CREATE_ARGS="--keypair-name ${SSH_KEY_PAIR} --ami ${AUTOK3S_AMI} \
                --instance-type ${AUTOK3S_INSTANCE_TYPE} \
                --region ${AUTOK3S_REGION} --request-spot-instance \
                --root-size 50 --security-group ${AUTOK3S_SECURITY_GROUP} \
                --volume-type ${AUTOK3S_VOLUME_TYPE} \
                --vpc-id ${AUTOK3S_VPC} --zone ${AUTOK3S_ZONE} \
                --k3s-install-script="https://rancher-mirror.rancher.cn/k3s/k3s-install.sh" \
                --system-default-registry=registry.rancher.cn \
                --install-env "INSTALL_K3S_MIRROR=cn" \
                --user-data-path /tmp/userdata.sh"
            ;;
        tencent)
            export CVM_SECRET_ID=${TENCENT_ACCESS_KEY_ID}
            export CVM_SECRET_KEY=${TENCENT_ACCESS_KEY_SECRET}
            AUTOK3S_CREATE_ARGS="--keypair-id ${SSH_KEY_PAIR} \
                --image ${AUTOK3S_AMI} \
                --instance-type ${AUTOK3S_INSTANCE_TYPE} \
                --region ${AUTOK3S_REGION} \
                --spot --disk-size 50 --security-group ${AUTOK3S_SECURITY_GROUP} \
                --disk-category ${AUTOK3S_VOLUME_TYPE} --vpc ${AUTOK3S_VPC} \
                --subnet ${AUTOK3S_SUBNET} --zone ${AUTOK3S_ZONE} \
                --system-default-registry=registry.rancher.cn \
                --internet-max-bandwidth-out=100 \
                --k3s-install-script "https://get.k3s.io" \
                --user-data-path /tmp/userdata.sh"
            ;;
        alibaba)
            export ECS_ACCESS_KEY_ID=${ALIYUN_ACCESS_KEY_ID}
            export ECS_ACCESS_KEY_SECRET=${ALIYUN_SECRET_ACCESS_KEY}
            AUTOK3S_CREATE_ARGS="--key-pair ${SSH_KEY_PAIR} \
                --image ${AUTOK3S_AMI} \
                --instance-type ${AUTOK3S_INSTANCE_TYPE} \
                --region ${AUTOK3S_REGION} \
                --disk-size 50 --security-group ${AUTOK3S_SECURITY_GROUP} \
                --disk-category ${AUTOK3S_VOLUME_TYPE} --v-switch ${AUTOK3S_VPC} \
                --zone ${AUTOK3S_ZONE} --internet-max-bandwidth-out=100 \
                --system-default-registry=registry.rancher.cn \
                --user-data-path /tmp/userdata.sh"
            ;;
    esac
}

get_rpm_config() {
    local external_ip=$(autok3s describe -n ${RPM_LOCAL_NAME} -p ${AUTOK3S_PROVIDER} | awk -F'[][]' '/external-ip/ {print $2}')
    echo "::add-mask::$external_ip"
    local server_url=$external_ip:30443
    echo "::add-mask::$server_url"
    local login_url="https://$server_url/v3-public/localProviders/local?action=login"
    local password=${ADMIN_PWD}
    local response=$(curl -s --insecure -L -X POST "$login_url" \
    -H 'Content-Type: application/json' \
    -d '{
        "username": "admin",
        "password": "'$password'",
        "responseType": "json"
    }')
    local token=$(echo "$response" | jq -r '.token')
    echo "::add-mask::$password"
    echo "::add-mask::$token"

    # set server-url
    local setting_server_url="https://$server_url/v3/settings/server-url"
    local auth_header="Authorization: Bearer $token"
    local server_url_response=$(curl -s --insecure -L -X GET "$setting_server_url" \
                            --header "$auth_header" \
                            --header 'Accept: application/json' \
                            --header 'Content-Type: application/json')

    local server_url_body=$(echo "$server_url_response" | jq --arg server_url "https://$server_url" '.value = $server_url')
    echo "setting server_url for RPM: $server_url_body"

    local response_code=$(curl -s -o /dev/null --insecure -w "%{http_code}" -L -X PUT "$setting_server_url" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -H "$auth_header" \
        -d "$server_url_body")

        if [ "$response_code" -ne 200 ]; then
        echo "failed to set server_url for RPM"
        exit 1
        fi

    local CONFIG_FILE_BASE="config_panda_base"
    cat << EOF > ${CONFIG_FILE_BASE}
rancher:
host: "$server_url"
adminToken: "$token"
cleanup: true
insecure: true
EOF

    RANCHER_SERVER_URL="$server_url"
    RANCHER_SERVER_TOKEN="$token"
}

prepare_environment() {
    cp data/registries.yaml /tmp/registries.yaml
    cp data/userdata.sh /tmp/userdata.sh

    sed -i -e 's/DOCKERHUB_USERNAME/'"${DOCKERHUB_USERNAME:-}"'/g' \
        -e 's/DOCKERHUB_PASSWORD/'"${DOCKERHUB_PASSWORD:-}"'/g' \
        -e 's/PRIME_REGISTRY_USERNAME/'"${PRIME_REGISTRY_USERNAME:-}"'/g' \
        -e 's/PRIME_REGISTRY_PASSWORD/'"${PRIME_REGISTRY_PASSWORD:-}"'/g' \
        /tmp/registries.yaml

    sed -i -e 's/$RPM_VERSION/'"${RPM_VERSION}"'/g' \
        -e 's/$ADMIN_PWD/'"${ADMIN_PWD:-RancherForFun}"'/g' \
        -e 's/$AUTOK3S_PROVIDER/'"${AUTOK3S_PROVIDER}"'/g' \
        -e 's/$DOCKERHUB_USERNAME/'"${DOCKERHUB_USERNAME:-}"'/g' \
        /tmp/userdata.sh

    # Prepare AutoK3s ssh private key
    sudo mkdir -p /opt/config/autok3s
    sudo mkdir -p /opt/config/autok3s
    sudo chmod 777 /opt/config/autok3s
    touch /opt/config/autok3s/$SSH_KEY_NAME
    cat > /opt/config/autok3s/$SSH_KEY_NAME << EOT
$SSH_SECRET_KEY
EOT
    chmod 600 /opt/config/autok3s/$SSH_KEY_NAME

    echo
    echo "prepare: Done"
}

wait_rpm_server_ready() {
    local AUTOK3S_CONTEXT=${AUTOK3S_REGION}.${AUTOK3S_PROVIDER}
    autok3s kubectl config use-context ${RPM_LOCAL_NAME}.${AUTOK3S_CONTEXT}

    # Wait for rancher server
    local status=''
    local count=0
    while [ "$status" != "1" ]; do
        sleep 10
        echo "-----------------------------------"
        echo "Waiting for the Rancher Deployment to become available..."
        autok3s kubectl -n cattle-system get deployment || true
        echo

        status=$(autok3s kubectl -n cattle-system get deployment rancher -o=jsonpath='{.status.availableReplicas}' || true)
        count=$((count+1))

        if [[ $count -gt 120 ]]; then
            # wait for 20 minutes
            echo "Timeout waiting for rancher deployment..."
            exit 1
        fi
    done

    # Wait for rancher webhook
    status=''
    count=0
    while [ "$status" != "1" ]; do
        sleep 10
        echo "-----------------------------------"
        echo "Waiting for Rancher Webhook Deployment ready..."
        autok3s kubectl -n cattle-system get deployment || true
        echo

        status=$(autok3s kubectl -n cattle-system get deployment rancher-webhook -o=jsonpath='{.status.availableReplicas}' || true)
        count=$((count+1))

        if [[ $count -gt 60 ]]; then
            # wait for 10 minutes
            echo "Timeout waiting for rancher webhook deployment..."
            exit 1
        fi
    done

    echo "Rancher Server is now available!"
}
