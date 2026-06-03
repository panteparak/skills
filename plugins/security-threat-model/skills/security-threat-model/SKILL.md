---
name: security-threat-model
description: Create a threat model for a system or feature using STRIDE methodology. Use when designing or reviewing system security architecture.
argument-hint: "[system-or-feature-description]"
---

# Threat Modeling (STRIDE)

Create a threat model for: **$ARGUMENTS**

## Process

1. **Understand the system** — read code, docs, architecture diagrams
2. **Identify assets** — what are we protecting?
3. **Map data flows** — how does data move through the system?
4. **Apply STRIDE** — identify threats per component
5. **Assess risk** — likelihood × impact
6. **Recommend mitigations** — prioritized by risk

## Step 1: System Decomposition

Identify and document:
- **Entry points**: APIs, UI, webhooks, message queues, cron jobs
- **Assets**: User data, credentials, payment info, business data
- **Trust boundaries**: Where trust level changes (public → authenticated → admin)
- **Data stores**: Databases, caches, file systems, external services
- **External dependencies**: Third-party APIs, CDNs, auth providers

## Step 2: Data Flow Diagram

```
[User] → [CDN/WAF] → [Load Balancer] → [API Gateway]
                                              │
                      ┌───────────────────────┤
                      ▼                       ▼
               [Auth Service]          [App Service]
                      │                       │
                      ▼                       ▼
               [User DB]              [App DB] [Cache]
                                              │
                                              ▼
                                      [External API]
```

Mark trust boundaries with dotted lines.

## Step 3: STRIDE Analysis

Apply each category to every component and data flow:

### S — Spoofing (Authentication)
Can an attacker pretend to be someone else?
- Stolen session tokens
- Forged API keys
- Replayed authentication
- Missing mutual TLS between services

### T — Tampering (Integrity)
Can an attacker modify data in transit or at rest?
- Man-in-the-middle attacks (no TLS)
- SQL injection modifying data
- Unsigned webhooks
- Missing integrity checks on file uploads

### R — Repudiation (Non-repudiation)
Can an attacker deny performing an action?
- Missing audit logs
- No tamper-proof logging
- Actions without authentication
- Missing transaction records

### I — Information Disclosure (Confidentiality)
Can an attacker access data they shouldn't?
- Error messages revealing internals
- Logs containing sensitive data
- Missing encryption at rest
- IDOR exposing other users' data
- Directory traversal

### D — Denial of Service (Availability)
Can an attacker make the system unavailable?
- No rate limiting
- Unbounded queries (missing pagination)
- Resource exhaustion (large file uploads)
- Dependency on single point of failure

### E — Elevation of Privilege (Authorization)
Can an attacker gain higher permissions?
- Missing server-side authorization checks
- Role manipulation in JWT tokens
- Admin endpoints without auth
- Privilege escalation via API parameter tampering

## Step 4: Risk Assessment Matrix

| Threat | Likelihood | Impact | Risk | Priority |
|--------|-----------|--------|------|----------|
| SQL injection in search | Medium | Critical | High | P1 |
| IDOR on user endpoints | High | High | Critical | P0 |
| DDoS on public API | Medium | Medium | Medium | P2 |

**Risk = Likelihood × Impact**

## Step 5: Mitigation Recommendations

For each threat, provide:
1. **Recommended mitigation** (technical control)
2. **Implementation effort** (Low/Medium/High)
3. **Priority** (P0=immediate, P1=sprint, P2=backlog)

## Output Template

```markdown
# Threat Model: [System Name]
**Date**: YYYY-MM-DD
**Author**: [name]
**Version**: 1.0

## System Overview
[Brief description and data flow diagram]

## Assets
1. [Asset 1] — [classification: public/internal/confidential/restricted]

## Trust Boundaries
1. [Boundary 1] — [what changes across this boundary]

## Threats (STRIDE)

### CRITICAL
| ID | Category | Component | Threat | Mitigation | Status |
|----|----------|-----------|--------|------------|--------|
| T-001 | Spoofing | Auth API | Token replay attack | Implement token binding | Open |

### HIGH
...

### MEDIUM
...

## Recommendations Summary
1. [P0] Implement [mitigation] for [threat]
2. [P1] Add [control] to [component]

## Residual Risks
- [Risks accepted with justification]
```

## Rules
- Every data flow crossing a trust boundary needs a threat
- STRIDE applies to components AND data flows
- Critical/High threats must have mitigations before deployment
- Threat models are living documents — update with architecture changes
- Include positive security controls already in place
