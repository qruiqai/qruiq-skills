---
name: qruiq-github-ci
description: |
  Add GitHub Actions CI/CD pipeline that builds Docker images, pushes to Tencent TCR, and deploys to TKE.
  Tag-triggered: dev-tag/v* for dev, v* for production. PR triggers lint+typecheck only,
  on GitHub's runner or, with one repository variable, on the organisation's own runner pool.
  Use when asked to "add CI/CD", "setup GitHub Actions", "auto deploy", or "add pipeline".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---

# qruiq-github-ci

> Tag-triggered CI/CD: push tag → build Docker image → push to TCR → deploy to TKE.

## Prerequisites

**Check before proceeding. Stop and prompt user if any fail:**

### 1. Detect user shell

```bash
echo $SHELL
```

### 2. Verify dependencies

| Command | Check | If missing |
|---|---|---|
| `gh` | `command -v gh` | `brew install gh` |
| `gh` logged in | `gh auth status` | `gh auth login` |
| `git` | `command -v git` | Install git |

### 3. Auto-detect parameters

```bash
gh api user --jq .login
gh api user/orgs --jq '.[].login'
git remote get-url origin 2>/dev/null
cat package.json | grep '"name"'
cat ~/.kube/config | base64 | tr -d '\n'
echo $TCR_USERNAME; echo $TCR_PASSWORD
```

## Parameters

**Auto-detect first, only ask user for values that cannot be detected.**

| Parameter | Required | Auto-detect method | Example |
|---|---|---|---|
| `APP_NAME` | Yes | `package.json` name field | `my-app` |
| `TCR_NAMESPACE` | Yes | `.env` files or default `qruiq` | `qruiq` |
| `GITHUB_ORG` | Yes | `gh api user/orgs` — let user pick | `my-org` |
| `DOMAIN` | No | `k8s/ingress.yaml` host field | `my-app.qruiq.app` |
| `TCR_USERNAME` | Yes | `$TCR_USERNAME` env var or `.env` | `100012345678` |
| `TCR_PASSWORD` | Yes | `$TCR_PASSWORD` env var or `.env` | `xxx` |
| `KUBE_CONFIG_DEV` | Yes | `cat ~/.kube/config \| base64` | `LS0t...` |

## Steps

**Execute all steps directly. Do not list as TODOs.**

### 1. Copy template files

```bash
mkdir -p .github/workflows
cp ~/.qruiq/skills/skills/qruiq-github-ci/template/.github/workflows/deploy-tke.yml .github/workflows/
cp ~/.qruiq/skills/skills/qruiq-github-ci/template/Dockerfile .
```

### 2. Replace placeholders in workflow

```bash
sed -i '' "s/__APP_NAME__/<APP_NAME>/g" .github/workflows/deploy-tke.yml
sed -i '' "s/__TCR_NAMESPACE__/<TCR_NAMESPACE>/g" .github/workflows/deploy-tke.yml
sed -i '' "s/__IMAGE_NAME__/<APP_NAME>/g" .github/workflows/deploy-tke.yml
sed -i '' "s/__DOMAIN__/<DOMAIN>/g" .github/workflows/deploy-tke.yml
```

### 3. Enable standalone output in `next.config.mjs`

```mjs
const nextConfig = {
  output: "standalone",
};
export default nextConfig;
```

### 4. Ensure `public/` has a file (prevent Docker build failure)

```bash
touch public/.gitkeep
```

### 5. Create GitHub repo and push

```bash
gh repo create <GITHUB_ORG>/<APP_NAME> --private
git remote add origin https://github.com/<GITHUB_ORG>/<APP_NAME>.git
git add .
git commit -m "chore: init project"
git push -u origin main
```

### 6. Configure GitHub Actions Secrets

**First, check if the org already has these secrets configured. Skip any that already exist at org level (the repo will inherit them automatically). Only set the missing ones at the repo level — and only ask the user for values that are still missing after this check.**

```bash
# List org-level secrets (requires admin:org scope; if it errors with 403, fall back to repo-level for all)
gh secret list --org <GITHUB_ORG> 2>/dev/null
```

For each of `TCR_USERNAME`, `TCR_PASSWORD`, `KUBE_CONFIG_DEV`, `KUBE_CONFIG_PROD`:
- If present in org-level list **and** visibility covers this repo (`all`, `private`, or `selected` with this repo included) → skip, the repo inherits it.
- If missing → ask the user for the value (unless already auto-detected) and set at repo level:

```bash
gh secret set <SECRET_NAME> --repo <GITHUB_ORG>/<APP_NAME> --body "<VALUE>"
```

If `gh secret list --org` returns 403 (token lacks `admin:org` read), tell the user: "Can't read org secrets — they may already be configured at org level. Skip repo secrets and rely on org inheritance, or provide values to set at repo level?" before falling back.

### 7. Verify secrets

```bash
gh secret list --repo <GITHUB_ORG>/<APP_NAME>      # repo-level
gh secret list --org <GITHUB_ORG> 2>/dev/null      # org-level (inherited)
```

### 8. Trigger first dev deploy

```bash
git tag dev-tag/v0.1.0
git push origin dev-tag/v0.1.0
```

Wait ~30s then check:
```bash
gh run list --repo <GITHUB_ORG>/<APP_NAME> --limit 5
```

### 9. Optional: run the pull request tests on our own runner pool

Only for a **private repository of the `qruiqai` organisation**: the pool is registered with that organisation and serves its private repositories. Anywhere else, skip this step; the `test` job then runs on GitHub's runner.

The template's `test` job reads the repository variable `CI_POOL_RUNNER` on pull requests. Nothing is set in a new repository. To send the job to the pool:

```bash
gh variable set CI_POOL_RUNNER --repo <GITHUB_ORG>/<APP_NAME> --body qruiq-pool-linux-6g
```

Then open a pull request and see that `Run Tests` passes there. The job gets a fresh arm64 Linux VM (4 cores, 6 GiB), which is destroyed afterwards. What to know:

- The pool's machines are arm64 and faster than GitHub's runners. A test that assumes x86-64, or that relies on a few milliseconds passing between two steps, can fail there. When the suite grows beyond lint and the type check, let the whole of it pass on the pool once before relying on it (`qruiqai/ci-runners`, `docs/onboarding.md`).
- While no host of the pool takes jobs, a job that names it waits instead of failing. To go back to GitHub's runner, delete the variable; no workflow change is needed:

```bash
gh variable delete CI_POOL_RUNNER --repo <GITHUB_ORG>/<APP_NAME>
```

- `build` and the deploy jobs are never sent to the pool: they carry the registry's and the clusters' secrets, and the image is built for `linux/amd64`. If `test` is later made to run on tag pushes too, the template's `runs-on` keeps those runs on GitHub's runner.

## Tag conventions

| Tag format | Target environment |
|---|---|
| `dev-tag/v0.1.0` | Dev |
| `v1.0.0` | Production |
| PR to `main`/`develop` | Tests only, no deploy |

## Pipeline flow

```
push tag (v* / dev-tag/v*)
    │
    ├─ test (PR only): lint + tsc --noEmit   (GitHub's runner, or our pool: step 9)
    ├─ build: Docker image → push to TCR
    │
    ├─ deploy-dev        (tag: dev-tag/v*)
    └─ deploy-production (tag: v*)
```

## Notes

- `deploy-dev` must use `always()` — when test job is skipped (tag push), GitHub Actions skips all downstream jobs by default
- Dev health check uses `kubectl exec` (not curl) — GitHub runner cannot reach cluster internal IPs
- `prisma db push` for dev (fast schema sync), `prisma migrate deploy` for prod (strict migration)
- `cache-from: type=gha` leverages GitHub Actions cache for faster Docker builds
- `platforms: linux/amd64` — TKE nodes are x86_64
- `test` has `timeout-minutes: 15` and uses `setup-node`'s yarn cache on GitHub's runners only (`runner.environment == 'github-hosted'`); both are for the runner pool of step 9 and change nothing on GitHub's runner

## GitHub Secrets required

| Secret | Description |
|---|---|
| `TCR_USERNAME` | TCR credentials username (Tencent CAM) |
| `TCR_PASSWORD` | TCR credentials password |
| `KUBE_CONFIG_DEV` | Dev cluster kubeconfig (base64) |
| `KUBE_CONFIG_PROD` | Production cluster kubeconfig (base64) |
