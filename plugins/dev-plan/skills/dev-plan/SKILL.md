---
name: dev-plan
description: Create or update project plan documentation — module maps, architecture docs, dependency diagrams, and development roadmaps. Use when documenting or planning project architecture.
argument-hint: "[project-path-or-action]"
disable-model-invocation: true
---

# Project Plan & Documentation

Create or update project documentation for: **$ARGUMENTS**

## Process

1. **Scan the project** — understand structure, modules, dependencies
2. **Generate documentation** — based on what the project needs
3. **Identify gaps** — what's missing or outdated
4. **Update** — create or refresh documentation

---

## Action 1: Module Map — Understand the Codebase

Scan the project and produce a module map:

### Module Discovery
```
For each top-level module/package/bounded context:
1. Name and purpose (1 sentence)
2. Key responsibilities
3. Public interface (what it exposes to other modules)
4. Dependencies (what it imports from other modules)
5. External dependencies (DB, cache, APIs, queues)
6. Test coverage status
```

### Output Format
```markdown
# Module Map

## Overview
[1-2 sentence project description]

## Modules

### <module-name>
- **Purpose**: [what this module does]
- **Layer**: [domain | application | infrastructure | transport]
- **Key Files**:
  - `path/to/file.py` — [role]
  - `path/to/file.py` — [role]
- **Exposes**: [public interfaces, APIs, events]
- **Depends On**: [other modules, external services]
- **Tests**: [test file locations, coverage status]

### <module-name>
...

## Dependency Graph
```
[A] ──→ [B] ──→ [C]
  \               ↑
   \──→ [D] ─────┘

Legend: arrow = "depends on"
```

## Cross-Cutting Concerns
- **Auth**: [how auth works across modules]
- **Error Handling**: [error handling pattern]
- **Logging**: [logging approach]
- **Config**: [how config is managed]
```

---

## Action 2: Architecture Document

Generate or update the project architecture document:

### Template: `docs/ARCHITECTURE.md`
```markdown
# Architecture

## System Overview
[What the system does, who it serves, key constraints]

## Architecture Style
[Clean Architecture / DDD / Hexagonal / MVC / Microservices]
[Why this style was chosen]

## High-Level Diagram
```
┌─────────────────────────────────────────┐
│              Transport Layer            │
│  (REST controllers, gRPC handlers)      │
├─────────────────────────────────────────┤
│            Application Layer            │
│  (Use cases, DTOs, orchestration)       │
├─────────────────────────────────────────┤
│              Domain Layer               │
│  (Entities, value objects, services)    │
├─────────────────────────────────────────┤
│          Infrastructure Layer           │
│  (DB repos, API clients, messaging)    │
└─────────────────────────────────────────┘
```

## Module Breakdown
[Reference Module Map or inline]

## Data Flow
[How a request flows through the system, end-to-end]

Example:
```
HTTP Request
  → Controller (validates input)
    → Use Case / Service (business logic)
      → Repository (data access)
        → Database
      ← Domain Entity
    ← Response DTO
  ← HTTP Response
```

## Key Patterns
- **Pattern 1**: [name] — [where used, why]
- **Pattern 2**: [name] — [where used, why]

## Data Model
[Key entities and their relationships]

## External Dependencies
| Service | Purpose | Failure Mode |
|---------|---------|--------------|
| PostgreSQL | Primary data store | Service degraded |
| Redis | Cache, sessions | Fallback to DB |
| Kafka | Event streaming | Retry with DLQ |

## Configuration
[How the app is configured — env vars, config files, secrets]

## Deployment
[How the app is deployed — Docker, K8s, cloud service]

## ADRs
See `docs/adr/` for architectural decisions:
- [ADR-001: Choice of database](docs/adr/0001-choice-of-database.md)
- [ADR-002: Event-driven notifications](docs/adr/0002-event-driven-notifications.md)
```

---

## Action 3: Development Roadmap

Create a structured development roadmap for upcoming work:

### Template: `docs/ROADMAP.md`
```markdown
# Development Roadmap

## Current Sprint / Milestone
| Priority | Task | Module | Status | Owner |
|----------|------|--------|--------|-------|
| P0 | [task] | [module] | [ ] Not started | |
| P0 | [task] | [module] | [~] In progress | |
| P1 | [task] | [module] | [x] Done | |

## Technical Debt
| Severity | Description | Module | Effort |
|----------|-------------|--------|--------|
| High | [debt item] | [module] | [S/M/L] |
| Medium | [debt item] | [module] | [S/M/L] |

## Future Considerations
- [Feature/improvement not yet planned]
```

---

## Action 4: Module Onboarding Guide

For each major module, generate a developer onboarding guide:

### Template: `docs/modules/<module-name>.md`
```markdown
# <Module Name> — Developer Guide

## What This Module Does
[2-3 sentences explaining the module's purpose and scope]

## Key Concepts
- **[Concept]**: [explanation]
- **[Concept]**: [explanation]

## Directory Structure
```
<module>/
├── domain/       # [what's here]
├── application/  # [what's here]
├── infrastructure/ # [what's here]
└── transport/    # [what's here]
```

## How to Add a New Feature
1. Create domain entity/value object in `domain/`
2. Define repository interface in `domain/`
3. Write failing unit test in `tests/`
4. Implement use case in `application/`
5. Implement repository in `infrastructure/`
6. Add API endpoint in `transport/`
7. Write integration test

## Common Patterns in This Module
- [Pattern] — [example with code snippet]

## Testing
- Run module tests: `make test-<module>`
- Test data setup: see `tests/factories.py`

## Gotchas
- [Non-obvious thing 1]
- [Non-obvious thing 2]
```

---

## Action 5: API Documentation Plan

If the project has APIs, ensure documentation is current:

### Checklist
- [ ] OpenAPI spec exists and matches implementation
- [ ] All endpoints documented with descriptions
- [ ] Request/response examples provided
- [ ] Error responses documented
- [ ] Authentication requirements documented
- [ ] Rate limiting documented
- [ ] Versioning strategy documented
- [ ] Swagger UI / ReDoc accessible in dev

---

## Action 6: Project Health Assessment

Audit the project and generate a health report:

```markdown
# Project Health Assessment

## Structure
- [ ] Clear module boundaries
- [ ] Consistent naming conventions
- [ ] No circular dependencies
- [ ] Domain layer free of infrastructure deps

## Testing
- [ ] Unit tests exist for business logic
- [ ] Integration tests exist for boundaries
- [ ] Test coverage measured
- [ ] Tests are deterministic

## Documentation
- [ ] README with setup, run, test instructions
- [ ] Architecture documented
- [ ] ADRs for key decisions
- [ ] API docs up to date

## Security
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] Auth/authz enforced
- [ ] Dependencies scanned

## CI/CD
- [ ] Linting in CI
- [ ] Tests in CI
- [ ] Build/deploy automated
- [ ] Branch protection rules

## Observability
- [ ] Structured logging
- [ ] Health checks
- [ ] Error tracking (Sentry or equivalent)

## Gaps Found
1. [gap] — [severity] — [recommendation]
```

---

## When to Use Each Action

| Situation | Action |
|-----------|--------|
| New team member joining | Module Map + Onboarding Guides |
| Starting a new project | Architecture Document + Module Map |
| Sprint planning | Development Roadmap |
| Before a major change | Module Map + ADR |
| Periodic maintenance | Project Health Assessment |
| API changes | API Documentation Plan |
| Tech debt review | Project Health Assessment + Roadmap |

## Rules
- Documentation lives in `docs/` — version controlled alongside code
- ADRs in `docs/adr/` — numbered sequentially, never edited after acceptance
- Keep docs concise — if it's over 2 pages, split it
- Diagrams use ASCII art (portable, diff-friendly) or Mermaid syntax
- Update docs when code changes — stale docs are worse than no docs
- Module map is the source of truth for "what exists and why"
