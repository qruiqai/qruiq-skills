---
name: qruiq-tke-deployment
description: |
  Add TKE Kubernetes deployment config: Namespace, ConfigMap, Secret, Deployment, Service, Ingress.
  Uses nginx ingress controller on Tencent TKE (Singapore cluster).
  Use when asked to "add K8s config", "deploy to TKE", "add deployment", or "setup Kubernetes".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---

# qruiq-tke-deployment

> Per-project Namespace isolation on Tencent TKE with nginx ingress. Based on production config from `ufcenter.xyz`.

## Prerequisites

**Check before proceeding. Stop and prompt user if any fail:**

### 1. Detect user shell

```bash
echo $SHELL
```

### 2. Verify dependencies

| Command | Check | If missing |
|---|---|---|
| `kubectl` | `command -v kubectl` | `brew install kubectl` |
| Cluster connected | `kubectl cluster-info` | Configure `~/.kube/config` |
| Correct context | `kubectl config current-context` | Show context, confirm with user |

### 3. Auto-detect parameters

```bash
kubectl config current-context
kubectl get namespaces --no-headers -o custom-columns=NAME:.metadata.name
kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
cat package.json | grep '"name"'
```

## Parameters

| Parameter | Required | Auto-detect method | Example |
|---|---|---|---|
| `APP_NAME` | Yes | `package.json` name field | `my-app` |
| `TCR_NAMESPACE` | Yes | `.env` files or default `qruiq` | `qruiq` |
| `DOMAIN` | No | `k8s/ingress.yaml` host field; leave `__DOMAIN__` if not found | `my-app.qruiq.app` |

## Steps

**Execute all steps directly. Do not list as TODOs. Pause at step 3 for user confirmation.**

### 1. Copy K8s config files

```bash
mkdir -p k8s/scripts
cp ~/.qruiq/skills/skills/qruiq-tke-deployment/template/k8s/*.yaml k8s/
cp ~/.qruiq/skills/skills/qruiq-tke-deployment/template/k8s/scripts/init-namespace.sh k8s/scripts/
chmod +x k8s/scripts/init-namespace.sh
```

### 2. Replace placeholders

```bash
sed -i '' "s/__APP_NAME__/<APP_NAME>/g" k8s/*.yaml
sed -i '' "s/__TCR_NAMESPACE__/<TCR_NAMESPACE>/g" k8s/*.yaml
sed -i '' "s/__IMAGE_NAME__/<APP_NAME>/g" k8s/*.yaml
sed -i '' "s/__DOMAIN__/<DOMAIN>/g" k8s/*.yaml
```

### 3. **[PAUSE]** Wait for user to initialize Namespace

Instruct user to prepare `.env.dev` (must contain `DATABASE_URL`, `NEXTAUTH_SECRET`, `NEXTAUTH_URL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`) and `TCR_USERNAME`/`TCR_PASSWORD`, then run:

```bash
export TCR_USERNAME=<tcr-username>
export TCR_PASSWORD=<tcr-password>
./k8s/scripts/init-namespace.sh <APP_NAME> dev
```

**Wait for user confirmation before continuing.**

### 4. Verify deployment

Execute all verification — do not leave for user to check.

**4a. Wait for pods**
```bash
kubectl rollout status deployment/<APP_NAME>-web -n <APP_NAME>-dev --timeout=5m
```

On failure, diagnose:
```bash
kubectl get pods -n <APP_NAME>-dev
kubectl describe pod -n <APP_NAME>-dev -l app=<APP_NAME>,component=web
kubectl logs -n <APP_NAME>-dev -l app=<APP_NAME>,component=web --tail=50
```

**4b. Health check (in-cluster)**
```bash
POD=$(kubectl get pod -n <APP_NAME>-dev -l app=<APP_NAME>,component=web -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n <APP_NAME>-dev $POD -- wget -q -O - http://localhost:3000/api/health
```

**4c. External access**

If DOMAIN configured:
```bash
curl -sf https://<DOMAIN>/api/health
```

If not, use LB IP + Host header:
```bash
LB_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -sf -H "Host: <APP_NAME>.qruiq.app" http://$LB_IP/api/health
```

**4d. Report results**

```
Deployment: SUCCESS / FAILED
Pod status: <Running / failure reason>
Health check: <passed / failure reason>
External access: <URL / pending items>

User action required:
- <DNS config, domain binding, etc.>
```

## Placeholder conventions

Template files use `__UPPERCASE__` placeholders:

| Placeholder | Description |
|---|---|
| `__APP_NAME__` | App name, also used as namespace prefix |
| `__TCR_NAMESPACE__` | TCR image namespace (default: `qruiq`) |
| `__IMAGE_NAME__` | Docker image name |
| `__DOMAIN__` | External domain |
| `__INGRESS_IP__` | TKE Ingress LB IP |

## Namespace convention

```
<project-name>-dev    # Dev/test environment
<project-name>-prod   # Production (optional)
```

## Resource manifest (deploy order)

1. **Namespace** — `k8s/namespace.yaml`
2. **TCR Secret** — `kubectl create secret docker-registry tcr-secret ...`
3. **ConfigMap** — `k8s/configmap.yaml`
4. **App Secret** — `kubectl create secret generic <app>-secrets --from-env-file=.env.dev`
5. **Deployment** — `k8s/deployment.yaml` (health probes on `/api/health:3000`)
6. **Service** — `k8s/service.yaml` (ClusterIP, port 80 → 3000)
7. **Ingress** — `k8s/ingress.yaml` (nginx ingress class)

## Cluster reference

| Item | Value |
|---|---|
| Cluster ID | `cls-rjk5qyka` |
| nginx Ingress LB IP | `43.173.190.227` — **use this for DNS** |
| Other CLB IP | `150.109.21.157` — **not nginx ingress, do not use** |
| TCR (Singapore) | `sgccr.ccs.tencentyun.com` |
| TCR Namespace | `qruiq` |
| Domain for new projects | `*.qruiq.app` (NS on Cloudflare) |

## Notes

- Only domains with NS on Cloudflare can route to nginx ingress. `qruiq.app` works; `ufcenter.xyz` (NS on afternic) does not.
- `kubectl get ingress` ADDRESS field may be inaccurate — always check `ingress-nginx-controller` Service EXTERNAL-IP.
- TKE CBS storage only supports `ReadWriteOnce`. For multi-pod shared storage, use CFS (NFS).

## Common operations

```bash
kubectl get pods -n <namespace>
kubectl logs -f deployment/<project>-web -n <namespace>
kubectl rollout restart deployment/<project>-web -n <namespace>
kubectl set image deployment/<project>-web web=<image>:<version> -n <namespace>
```
