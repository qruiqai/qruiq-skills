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
| `qruiq-cdb-create-db` | Create a schema + least-privilege account on an existing Tencent CDB MySQL, return a ready-to-use connection string |
| `qruiq-community-analyze` | Reddit community analysis: comment-timing windows + optional critic-prompt training for comment-ops |
| `qruiq-cos-storage` | Mount a Tencent COS bucket into a TKE pod as a ReadWriteMany PVC via the cosfs CSI driver |
| `qruiq-create-app` | Create a Next.js app from HeroUI template (Next.js 15 + Tailwind v4 + TypeScript) |
| `qruiq-deploy` | All-in-one orchestrator: local Next.js → live URL on TKE (drives CI, K8s, DB, verification) |
| `qruiq-domain-name` | Find an available, memorable .com domain by brainstorm → whois batch-check → brand-fit ranking |
| `qruiq-github-ci` | GitHub Actions CI/CD: build Docker → push TCR → deploy TKE |
| `qruiq-google-auth` | Add Google OAuth login with NextAuth.js v4 + PrismaAdapter |
| `qruiq-icon-generator` | Generate a project icon from the codebase, iterate to ≥ 90/100, derive favicon set + OG card + head snippet |
| `qruiq-mcp-init` | Add MCP server (OAuth2 + Streamable HTTP) to a Next.js app — Claude.ai / ChatGPT / Cursor compatible |
| `qruiq-optimize-skills` | Analyze session history and propose optimizations to skill definitions (user-confirmed writes) |
| `qruiq-review-ux` | Read-only audit of UX patterns + HeroUI design principles (no code changes) |
| `qruiq-tke-deployment` | TKE K8s config: Namespace, ConfigMap, Secret, Deployment, Service, Ingress |
| `qruiq-update` | Self-update: pull latest skills and re-run setup |

### Full project workflow

For a fresh project, the fastest path is the orchestrator:

```
/qruiq-domain-name      → Pick a .com
/qruiq-create-app       → Project skeleton
/qruiq-google-auth      → Layer Google OAuth (optional)
/qruiq-icon-generator   → Brand mark + favicon set
/qruiq-deploy           → CI + TKE + DB + live URL (delegates to /qruiq-github-ci, /qruiq-tke-deployment, /qruiq-cdb-create-db)
```

Each step also works standalone if you only need that layer.

## Structure

```
skills/
  qruiq-<name>/           # Each skill lives in its own dir with a SKILL.md
templates/
  SKILL.md.template       # Starter template for new skills
setup                     # Install/update script (symlinks skills/qruiq-*/ into ~/.claude and ~/.codex)
```
