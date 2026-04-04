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

## Structure

```
skills/
  qruiq-update/SKILL.md    # Self-update skill
  qruiq-.../SKILL.md       # Your skills here
templates/
  SKILL.md.template         # Starter template
setup                       # Install/update script
```
