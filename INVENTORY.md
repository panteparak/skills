# Claude Skills Inventory

Snapshot of everything that was installed globally on this machine before the
2026-06-03 full reset, with exact reinstall instructions. Raw registry files are
preserved under [`backup/registries/`](backup/registries/).

Three origin classes:

- **A. Marketplace plugins** — installed via `/plugin`, reinstallable from their source repos.
- **B. External standalone skills** — were symlinked from `~/.agents/skills`, sources in `.skill-lock.json`.
- **C. Self-authored skills** — local-origin only, no external source. Preserved in this repo (see [`plugins/`](plugins/)).

---

## A. Marketplace plugins

Reinstall a marketplace, then enable the plugin:

```bash
# in a Claude Code session
/plugin marketplace add anthropics/claude-plugins-official
/plugin install <plugin>@claude-plugins-official
```

| Plugin | Marketplace repo | State at snapshot |
|---|---|---|
| frontend-design | `anthropics/claude-plugins-official` | enabled |
| github | `anthropics/claude-plugins-official` | enabled |
| feature-dev | `anthropics/claude-plugins-official` | enabled |
| code-review | `anthropics/claude-plugins-official` | enabled |
| playwright | `anthropics/claude-plugins-official` | enabled |
| explanatory-output-style | `anthropics/claude-plugins-official` | enabled |
| pr-review-toolkit | `anthropics/claude-plugins-official` | enabled |
| serena | `anthropics/claude-plugins-official` | disabled |
| security-guidance | `anthropics/claude-plugins-official` | disabled |
| frontend-design | `anthropics/claude-code` | enabled (duplicate) |
| feature-dev | `anthropics/claude-code` | enabled (duplicate) |
| pr-review-toolkit | `anthropics/claude-code` | enabled (duplicate) |
| ui-ux-pro-max | `nextlevelbuilder/ui-ux-pro-max-skill` | enabled, project-scoped to `PayStream` |

> Note: `anthropics/claude-plugins-official` and `anthropics/claude-code` both
> shipped `frontend-design`, `feature-dev`, `pr-review-toolkit`. Pick one
> marketplace on reinstall to avoid the duplicate registration.

Marketplaces to re-add:

```bash
/plugin marketplace add anthropics/claude-plugins-official
/plugin marketplace add anthropics/claude-code
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
```

---

## B. External standalone skills (16)

These were installed by the `vercel-labs/skills` installer and symlinked from
`~/.agents/skills`. Reinstall with that installer (or clone the source repo and
copy the skill folder).

| Skill | Source repo |
|---|---|
| building-components | https://github.com/vercel/components.build.git |
| find-skills | https://github.com/vercel-labs/skills.git |
| component-architecture | https://github.com/sanky369/vibe-building-skills.git |
| solid | https://github.com/ramziddin/solid-skills.git |
| caveman | https://github.com/mattpocock/skills.git |
| diagnose | https://github.com/mattpocock/skills.git |
| grill-me | https://github.com/mattpocock/skills.git |
| grill-with-docs | https://github.com/mattpocock/skills.git |
| improve-codebase-architecture | https://github.com/mattpocock/skills.git |
| setup-matt-pocock-skills | https://github.com/mattpocock/skills.git |
| tdd | https://github.com/mattpocock/skills.git |
| to-issues | https://github.com/mattpocock/skills.git |
| to-prd | https://github.com/mattpocock/skills.git |
| triage | https://github.com/mattpocock/skills.git |
| write-a-skill | https://github.com/mattpocock/skills.git |
| zoom-out | https://github.com/mattpocock/skills.git |

Full per-skill metadata (commit hashes, install paths, the `mattpocock-skills`
plugin name) is preserved in [`backup/registries/agents-skill-lock.json`](backup/registries/agents-skill-lock.json).

---

## C. Self-authored skills (42) — preserved in this repo

No external source — these are original work. Now packaged here as individual
plugins (see [`plugins/`](plugins/)). Listed for the record:

| Skill | Description |
|---|---|
| debug-backend | Systematically debug backend issues using structured root cause analysis. |
| debug-db | Debug database issues: slow queries, deadlocks, migration failures, data integrity. |
| debug-k8s | Debug Kubernetes issues: pod failures, networking, RBAC, operator problems. |
| design-system | Create or audit a design system with consistent components, tokens, patterns. |
| dev-api | Design/implement REST APIs using OpenAPI-first approach. |
| dev-ci-github | Create GitHub Actions CI/CD workflows. |
| dev-ci-gitlab | Create GitLab CI/CD pipelines. |
| dev-django | Develop Django + DRF features (services/selectors, TDD, sub-apps). |
| dev-dockerfile | Production-grade Dockerfiles (multi-stage, hardening, layer caching). |
| dev-event-driven | Event-driven architecture with Kafka/RabbitMQ/cloud messaging. |
| dev-flow | Structured dev workflow — Explore, Plan, Implement (TDD), Review, Document. |
| dev-flutter | Develop Flutter features (Riverpod, clean architecture, TDD). |
| dev-go | Develop Go services (clean architecture, TDD, idiomatic Go). |
| dev-helm | Create/modify Helm charts. |
| dev-k8s-operator | Develop K8s operator features (reconciliation, CRDs, testing). |
| dev-maintain | Audit/improve maintainability (SOLID, coupling, complexity, tech debt). |
| dev-nextjs | Develop Next.js + React + TS features (App Router, Server Components). |
| dev-observability | Structured logging, metrics, tracing with OpenTelemetry. |
| dev-plan | Project plan docs — module maps, architecture, roadmaps. |
| dev-springboot | Develop Spring Boot + Kotlin features (TDD, clean architecture). |
| doc-adr | Create Architecture Decision Records. |
| doc-flow | Comprehensive internal docs with Mermaid diagrams. |
| git-commit | Conventional commits with proper staging and pre-commit checks. |
| git-pr | Well-structured PRs via gh CLI. |
| init-django | Scaffold a new Django + DRF project (DDD, uv). |
| init-fastapi | Scaffold a new FastAPI project (clean architecture, async, uv). |
| init-flutter | Scaffold a new Flutter app (clean architecture, testing). |
| init-go | Scaffold a new Go service (clean architecture, DDD, TDD). |
| init-k8s-operator | Scaffold a new K8s operator (kubebuilder/operator-sdk). |
| init-nextjs | Scaffold a new Next.js + React + TS project. |
| init-springboot | Scaffold a new Spring Boot + Kotlin project (DDD, TDD). |
| init-terraform | Scaffold Terraform IaC (modules, state, env separation). |
| refactor-code | Systematic refactoring preserving behavior. |
| review-code | Thorough code review (architecture, correctness, security, perf, tests). |
| security-audit | Security audit (OWASP Top 10, injection, auth, secrets, data exposure). |
| security-threat-model | STRIDE threat model. |
| test-e2e | End-to-end tests (Playwright, Cypress, API-level). |
| test-generate | Generate test cases/suites for existing code. |
| test-integration | Integration tests (Testcontainers, real dependencies). |
| test-performance | Load/perf tests (k6, Locust). |
| test-unit | Unit tests following TDD. |
| ux-audit | UX audit (usability heuristics, accessibility, flow quality). |
