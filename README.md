# qruiq-skills

Centralized AI CLI skills for Claude Code and OpenAI Codex.

## Install

```bash
git clone https://github.com/qruiqai/qruiq-skills.git ~/.qruiq/skills && chmod +x ~/.qruiq/skills/setup && ~/.qruiq/skills/setup
```

## Update

```bash
cd ~/.qruiq/skills && git pull && ./setup
```

Or use the `/qruiq-update` skill inside Claude Code or Codex.

## Add a new skill

```bash
cp -r templates/SKILL.md.template skills/qruiq-myskill/SKILL.md
# Edit skills/qruiq-myskill/SKILL.md
./setup
```

## How it works

The `setup` script creates symlinks from each `skills/qruiq-*/` directory into:
- `~/.claude/skills/` (Claude Code)
- `~/.codex/skills/` (OpenAI Codex)

Both CLIs auto-discover skills by scanning for `SKILL.md` files in their skill directories.

## Skills

| Skill | Description |
|---|---|
| `qruiq-create-app` | Create a Next.js app from HeroUI template (Next.js 15 + Tailwind v4 + TypeScript) |
| `qruiq-google-auth` | Add Google OAuth login with NextAuth.js v4 + PrismaAdapter |
| `qruiq-github-ci` | GitHub Actions CI/CD: build Docker → push TCR → deploy TKE |
| `qruiq-tke-deployment` | TKE K8s config: Namespace, ConfigMap, Secret, Deployment, Service, Ingress |
| `qruiq-update` | Self-update: pull latest skills and re-run setup |

### Full project workflow

```
Step 1  /qruiq-create-app      → Project skeleton
Step 2  /qruiq-google-auth     → Layer Google OAuth
Step 3  /qruiq-github-ci       → Layer CI/CD pipeline
Step 4  /qruiq-tke-deployment  → Layer K8s deployment
Step 5  Push tag               → Deploy
```

## Structure

```
skills/
  qruiq-create-app/       # App skeleton (with template/)
  qruiq-google-auth/      # Google OAuth (with template/)
  qruiq-github-ci/        # CI/CD pipeline (with template/)
  qruiq-tke-deployment/   # K8s config (with template/)
  qruiq-update/           # Self-update
templates/
  SKILL.md.template       # Starter template for new skills
setup                     # Install/update script
```
