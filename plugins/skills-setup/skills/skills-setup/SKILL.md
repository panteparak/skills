---
name: skills-setup
description: Detect a project's stack and install matching popular Claude Code skills from a curated index. Use when setting up or onboarding a repo, or when the user asks to recommend/install skills for their project, stack, or language (Go, Next.js, Django, Angular, Flutter, Terraform, Kubernetes, etc.).
argument-hint: "[project-dir]"
---

# Skills Setup — stack-aware skill installer

Detect what a project is built with and install the right popular, community-maintained
skills for it. Recommend first, install on confirmation.

The catalog of skills and the detector live next to this file:
- `recommend-skills.py` — stack detector + installer (pure stdlib, no deps)
- `catalog.json` — the curated index (edit this to add/remove skills or stacks)

## Workflow

### 1. Pick the project
Use the argument as the project directory; otherwise the current working directory.

### 2. Detect + get recommendations
Run the bundled detector (it is in the same directory as this SKILL.md):

```bash
python3 "<this-skill-dir>/recommend-skills.py" "<project-dir>" --json
```

This returns detected stacks, a recommendation list (each with `id`, `type`, `reasons`,
`purpose`, `stars`, `available`, `command`), and known coverage `gaps`.

### 3. Present the recommendations (recommend-first — do NOT install yet)
Show the user:
- **Detected stacks** (e.g. "Go, K8s Operator, Security").
- **Recommended skills**, grouped into *to install* vs *already available*. For each: the id,
  why it was picked (`reasons`), a one-line purpose, and ★ stars. Mark the three install types:
  - `marketplace` → enabled via the project's `.claude/settings.json` (activates next session)
  - `skills-cli` → installed now via `npx skills add ...`
  - `manual` → you must clone/copy it (show the URL)
- **Coverage gaps** so the user knows what has no good skill (Docker, OTel app-instrumentation,
  Kafka, dedicated Go-DDD).

Then ask which to install — default to all *to install* items; let the user drop any.

### 4. Install (only after the user confirms)
- **Marketplace skills** → write them into `<project>/.claude/settings.json` (deep-merge, never
  clobbers existing keys):
  ```bash
  python3 "<this-skill-dir>/recommend-skills.py" "<project-dir>" --write [--only id1,id2] [--exclude id3]
  ```
- **skills-cli skills** → run each printed `npx skills add ...` command **in the project dir**.
- **manual skills** → show the repo URL and tell the user to clone/copy (do not auto-run).

### 5. Tell the user what happens next
- Marketplace plugins install automatically when Claude Code next opens the repo (or after a
  reload) — they are enabled in `.claude/settings.json`, not installed in this session.
- skills-cli skills are available immediately.
- Verify with `claude plugin list` in the project.

## Rules
- **Never install without confirmation.** Always show the recommendation and the reasons first.
- **Respect what's already there.** Items marked `available` (registered/installed) are skipped —
  don't re-install them.
- **Don't hand-edit `.claude/settings.json`** for marketplace skills — use `--write` so the
  merge stays safe. Only the two keys `extraKnownMarketplaces` and `enabledPlugins` are touched.
- **Honesty over coverage.** Surface the `gaps` rather than recommending a weak/abandoned skill.
- **To extend the catalog**, edit `catalog.json` (add a `skills` entry + a `stacks` detection
  rule). No code change needed.
