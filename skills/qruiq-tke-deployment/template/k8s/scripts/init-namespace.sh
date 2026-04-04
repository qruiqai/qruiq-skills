#!/bin/bash
# 初始化新项目的 Kubernetes Namespace
# 用法：./init-namespace.sh <app-name> <env>
# 示例：./init-namespace.sh myapp dev

set -e

APP=$1
ENV=${2:-dev}
NAMESPACE="${APP}-${ENV}"

if [ -z "$APP" ]; then
  echo "Usage: $0 <app-name> [env]"
  exit 1
fi

if [ -z "$TCR_USERNAME" ] || [ -z "$TCR_PASSWORD" ]; then
  echo "Error: TCR_USERNAME and TCR_PASSWORD env vars must be set"
  exit 1
fi

echo "Initializing namespace: $NAMESPACE"

kubectl create namespace $NAMESPACE 2>/dev/null || echo "Namespace already exists"

kubectl create secret docker-registry tcr-secret \
  --docker-server=sgccr.ccs.tencentyun.com \
  --docker-username=$TCR_USERNAME \
  --docker-password=$TCR_PASSWORD \
  --namespace=$NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

if [ -f ".env.${ENV}" ]; then
  kubectl create secret generic ${APP}-secrets \
    --from-env-file=.env.${ENV} \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -
else
  echo "Warning: .env.${ENV} not found, skipping secret creation"
fi

for f in k8s/configmap.yaml k8s/deployment.yaml k8s/service.yaml k8s/ingress.yaml; do
  if [ -f "$f" ]; then
    sed "s/__APP_NAME__/$APP/g; s/__TCR_NAMESPACE__/${TCR_NAMESPACE:-qruiq}/g; s/__IMAGE_NAME__/$APP/g; s/__DOMAIN__/${DOMAIN:-localhost}/g" \
      "$f" | kubectl apply -f -
  fi
done

echo ""
echo "Done! Namespace $NAMESPACE initialized."
echo "Check status: kubectl get all -n $NAMESPACE"
