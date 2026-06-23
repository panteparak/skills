# panteparak-skills

A **curated index of popular Claude Code skills** plus a **stack-aware installer**.

Point it at any project; it detects the stack (Go, Next.js, Django, Angular, Flutter,
Terraform, Kubernetes, …) and installs the matching popular, community-maintained skills —
**from source, nothing vendored**. Recommend first, install on confirmation.

> **History:** this repo previously held 42 self-authored skills. A 2026 audit found most were
> redundant with skills already installed (`solid`, `tdd`, `review`, built-in `/code-review`),
> rotted by hard version pins (Spring Boot 3.4.3, Node 20, OWASP 2021), or shipped broken
> example code — so it was reset to **pure curation**. The originals remain in git history.

## What's here

```
plugins/skills-setup/skills/skills-setup/
├── SKILL.md             # the entry-point installer skill
├── recommend-skills.py  # stdlib stack detector + installer (no deps)
└── catalog.json         # the curated index — EDIT THIS to add/remove skills or stacks
.claude-plugin/marketplace.json   # generated (1-plugin marketplace)
scripts/generate-manifests.py     # regenerates manifests from SKILL.md
INVENTORY.md                      # historical record of the pre-reset setup
```

## Use it

```bash
# once
/plugin marketplace add panteparak/skills
/plugin install skills-setup@panteparak-skills
```

Then in any repo, invoke **`/skills-setup`** — it detects the stack, lists the recommended
skills with reasons, and installs them on your confirmation (marketplace skills go into the
repo's `.claude/settings.json`; `npx skills add` skills install immediately; manual ones are
shown with their URL).

Or run the detector directly, no install:

```bash
python3 plugins/skills-setup/skills/skills-setup/recommend-skills.py /path/to/project
python3 .../recommend-skills.py /path/to/project --json      # machine-readable
python3 .../recommend-skills.py /path/to/project --write      # merge marketplace skills into .claude/settings.json
```

## The catalog (verified 2026-06-23)

**Universal (every repo):** `superpowers` · `ponytail` · `anthropic-skills` ·
`addy-agent-skills` · `solid` · `wshobson-agents`

| Stack | Skills |
|---|---|
| Go | `cc-skills-golang` |
| Kotlin / Spring | `spring-boot` |
| Django / DRF | `jeffallan-skills` |
| FastAPI | `jeffallan-skills` |
| Next.js / React | `vercel-react` · `ui-ux-pro-max` |
| Angular | `angular` · `ui-ux-pro-max` |
| Flutter | `vgv-flutter` |
| Kubernetes / Helm | `k8s` |
| K8s operator (kubebuilder) | `k8s-operator` · `k8s` |
| Terraform / IaC | `terraform` · `hashicorp` |
| Security (always offered) | `trailofbits-sec` · `owasp` |

Each entry records its repo, install type (`marketplace` / `skills-cli` / `manual`), exact
install command, tags, purpose, stars, and license. See
[`catalog.json`](plugins/skills-setup/skills/skills-setup/catalog.json).

## Extend it

- **Add a skill:** add an entry under `skills` in `catalog.json` (`repo`, `type`, `install`/
  `skillsCli`, `tags`, `purpose`), then list its id under `universal` or a stack's `skills`.
- **Add a stack:** add a `stacks` entry with a `detect` predicate. Predicates: `fileExists`,
  `glob`, `jsonDep`, `fileContains`, combined with `anyOf` / `allOf` / `noneOf` / `always`.

No code changes needed — the detector reads the JSON.

## Coverage gaps (no strong popular skill)

Docker, OpenTelemetry app-instrumentation, Kafka/event-driven, and a dedicated Go-DDD skill
have no well-maintained popular option — fall back to the multi-stack collections
(`jeffallan-skills`, `cc-skills-golang`) and per-repo `CLAUDE.md` conventions.

## References

- https://github.com/ramziddin/solid-skills
- https://blog.codacy.com/what-is-clean-code

### K8S Operators
- https://github.com/redhat-cop/vault-config-operator
