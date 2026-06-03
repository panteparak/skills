---
name: doc-adr
description: Create Architecture Decision Records (ADRs) documenting significant technical decisions with context, alternatives, and consequences. Use when making or documenting architectural choices.
argument-hint: "[decision-title]"
disable-model-invocation: true
---

# Architecture Decision Record

Create an ADR for: **$ARGUMENTS**

## Process

1. **Understand the decision context** — what problem are we solving?
2. **Identify alternatives** — what options were considered?
3. **Evaluate trade-offs** — pros, cons, risks of each option
4. **Document the decision** — using the template below
5. **Save to `docs/adr/`** — with sequential numbering

## ADR Template

Create a file at `docs/adr/NNNN-<title-in-kebab-case>.md`:

```markdown
# NNNN. <Decision Title>

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded by [NNNN]
**Deciders**: [who was involved]

## Context

What is the issue we're facing? What forces are at play?
Describe the technical and business context that makes this decision necessary.
Include constraints, requirements, and any relevant background.

## Decision

What is the change we're making?
State the decision clearly and concisely in 1-3 sentences.
Use active voice: "We will use X for Y because Z."

## Alternatives Considered

### Option A: [Name]
- **Pros**: ...
- **Cons**: ...
- **Risk**: ...

### Option B: [Name] (Chosen)
- **Pros**: ...
- **Cons**: ...
- **Risk**: ...

### Option C: [Name]
- **Pros**: ...
- **Cons**: ...
- **Risk**: ...

## Consequences

### Positive
- [What becomes easier or better]

### Negative
- [What becomes harder or worse]
- [Technical debt incurred]

### Risks
- [What could go wrong]
- [Mitigation strategies]

## References

- [Links to relevant docs, RFCs, discussions, PRs]
```

## When to Write an ADR

Write an ADR when:
- Choosing a framework, library, or language for a new component
- Deciding on architecture patterns (monolith vs microservices, sync vs async)
- Changing database technology or schema design approach
- Choosing authentication/authorization strategy
- Defining API contract patterns (REST vs GraphQL, versioning strategy)
- Making deployment/infrastructure decisions (K8s vs serverless)
- Deciding on testing strategy changes
- Any decision that is hard to reverse or affects multiple teams

Do NOT write an ADR for:
- Trivial decisions (variable naming, import ordering)
- Decisions fully dictated by existing conventions
- Temporary workarounds (track these as tech debt instead)

## Example ADRs

### 0001 — Record Architecture Decisions
```markdown
# 0001. Record Architecture Decisions

**Date**: 2024-01-15
**Status**: Accepted

## Context
We need to record significant architectural decisions so that
future team members understand why things are the way they are.

## Decision
We will use Architecture Decision Records (ADRs) as described
by Michael Nygard. ADRs will be stored in `docs/adr/` and
numbered sequentially.

## Consequences
### Positive
- New team members can understand historical context
- Decisions are explicit and searchable
### Negative
- Requires discipline to maintain
```

### 0002 — Use PostgreSQL as Primary Database
```markdown
# 0002. Use PostgreSQL as Primary Database

**Date**: 2024-01-20
**Status**: Accepted
**Deciders**: Backend team

## Context
We need a primary database for our order management system.
Requirements: ACID transactions, JSON support, full-text search,
strong ecosystem, proven at scale.

## Decision
We will use PostgreSQL 16 as our primary database.

## Alternatives Considered

### MySQL 8
- **Pros**: Wide adoption, good tooling
- **Cons**: Weaker JSON support, no native full-text search ranking
- **Risk**: May need ElasticSearch sooner

### MongoDB
- **Pros**: Flexible schema, good for rapid iteration
- **Cons**: No ACID across documents, eventual consistency complexity
- **Risk**: Data integrity issues in financial operations

### PostgreSQL 16 (Chosen)
- **Pros**: ACID, excellent JSON (jsonb), full-text search, CTEs, proven at scale
- **Cons**: Slightly more complex replication setup than MySQL
- **Risk**: Team needs training on advanced PG features

## Consequences
### Positive
- Single database for relational + JSON + search needs
- Strong migration tooling (Flyway/Alembic)
### Negative
- Team needs PostgreSQL-specific training
- Hosting costs slightly higher than MySQL
```

## File Organization

```
docs/
└── adr/
    ├── 0001-record-architecture-decisions.md
    ├── 0002-use-postgresql-as-primary-database.md
    ├── 0003-use-event-driven-architecture-for-notifications.md
    └── template.md
```

## Rules
- ADRs are **immutable** once accepted — create a new ADR to supersede, don't edit old ones
- Keep ADRs **short** — 1-2 pages maximum
- Focus on **WHY**, not just WHAT
- Include **alternatives** — show you considered options
- Document **consequences** honestly — both positive and negative
- Number sequentially — don't reuse numbers
- Status transitions: Proposed → Accepted → (optionally) Deprecated/Superseded
