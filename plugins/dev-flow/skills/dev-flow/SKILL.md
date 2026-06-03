---
name: dev-flow
description: Complete structured development workflow — Explore, Plan, Implement (TDD), Review, Document. Use when developing any feature, fixing bugs, or making significant code changes. Replaces the old /epct command.
argument-hint: "[feature-or-task-description]"
---

# Structured Development Flow

Follow this complete development lifecycle for: **$ARGUMENTS**

You are acting as a Principal Software Engineer. Execute each phase fully before moving to the next. Do NOT skip phases. Provide output for each phase.

---

## Phase 1: EXPLORE — Understand Before You Touch

**Goal**: Build a complete mental model of the relevant codebase before writing any code.

### 1.1 Module Discovery
- Identify which modules/packages/bounded contexts are involved
- Map the dependency graph between affected modules
- Understand the data flow: entry point → handler → service → repository → DB

### 1.2 Existing Pattern Analysis
- Read existing code in the affected area thoroughly
- Identify established patterns (naming, structure, error handling)
- Find existing utilities, helpers, base classes that should be reused
- Check for existing tests to understand the testing approach

### 1.3 Architecture Understanding
- Identify the architecture style (DDD, clean arch, MVC, etc.)
- Map the layer boundaries: domain → application → infrastructure → transport
- Verify dependency direction (domain has no external deps)
- Check for cross-cutting concerns (auth, logging, error handling)

### 1.4 Dependency & Impact Assessment
- What other modules depend on code we're changing?
- What external dependencies are involved (DB, cache, APIs, queues)?
- Are there contracts (API specs, events, shared models) that constrain us?
- What could break?

### Explore Deliverable:
```
## Exploration Summary

### Affected Modules
- [module] — [role, what it does]

### Existing Patterns Found
- [pattern] — [where, how it works]

### Reusable Code
- [file:function] — [what it does, how we'll use it]

### Dependencies & Risks
- [dependency] — [impact if changed]

### Architecture Notes
- [key observation about structure]
```

---

## Phase 2: PLAN — Design Before You Build

**Goal**: Create a clear, reviewable implementation plan before writing production code.

### 2.1 Requirements Breakdown
- Break the task into discrete, testable work items
- Each item should be completable in one TDD cycle (test → implement → refactor)
- Order items by dependency (what must exist before what)

### 2.2 Interface Design
- Define the public API/interface of new code BEFORE implementation
- Design DTOs, request/response shapes, function signatures
- If API change: draft the OpenAPI spec changes first
- If DB change: draft the migration SQL first

### 2.3 Architecture Decision
- If trade-offs exist, document them as an ADR (use `/doc-adr`)
- Choose patterns that match existing codebase conventions
- Prefer the simplest solution that meets requirements

### 2.4 Test Strategy
- Identify what needs unit tests (domain logic, services)
- Identify what needs integration tests (DB, external APIs)
- Identify what needs E2E tests (critical user flows)
- Plan test data setup (factories, fixtures, seeds)

### Plan Deliverable:
```
## Implementation Plan

### Work Items (in order)
1. [ ] [item] — [what, where, test approach]
2. [ ] [item] — [what, where, test approach]
3. [ ] [item] — [what, where, test approach]

### Interface Design
- [function signature / API endpoint / event schema]

### Files to Create/Modify
- [file] — [what changes]

### Test Strategy
- Unit: [what to unit test]
- Integration: [what to integration test]
- E2E: [what to E2E test, if any]

### Risks & Mitigations
- [risk] → [mitigation]
```

---

## Phase 3: IMPLEMENT — TDD, One Work Item at a Time

**Goal**: Implement each work item using strict Test-Driven Development.

For EACH work item in the plan:

### 3.1 RED — Write Failing Test
```
1. Write a test that describes the desired behavior
2. The test MUST fail (proves it tests something real)
3. Test name describes behavior: "should reject order with empty items"
4. One assertion per test (or closely related group)
```

### 3.2 GREEN — Make It Pass
```
1. Write the MINIMUM production code to make the test pass
2. No extra features, no premature abstractions
3. It's OK to be ugly — we'll clean up in refactor
4. Run the test — it MUST pass
```

### 3.3 REFACTOR — Clean Up
```
1. Improve the code while keeping tests green
2. Extract methods, rename for clarity, remove duplication
3. Apply project conventions (naming, structure, patterns)
4. Run ALL tests — everything MUST still pass
```

### 3.4 Repeat
```
Move to the next work item. Repeat RED → GREEN → REFACTOR.
```

### Implementation Rules
- **Never write production code without a failing test first**
- **Never move to the next item until current item's tests all pass**
- **Commit after each successful RED-GREEN-REFACTOR cycle**
- Follow the project's established:
  - Naming conventions
  - Package/module structure
  - Error handling patterns
  - Logging patterns
  - Dependency injection approach

### Code Quality Checklist (per work item)
- [ ] Functions small and focused (single responsibility)
- [ ] Names reveal intent (no abbreviations, no generic names)
- [ ] No magic numbers/strings — use named constants
- [ ] Error handling is explicit and typed
- [ ] No commented-out code, no TODOs left behind
- [ ] Domain logic has no framework/infrastructure imports
- [ ] Input validation at system boundaries

---

## Phase 4: VERIFY — Comprehensive Quality Check

**Goal**: Ensure the implementation is correct, secure, performant, and maintainable.

### 4.1 Test Coverage Audit
Run all tests and verify:
- [ ] All new code paths are covered
- [ ] Edge cases tested (empty input, boundary values, nulls)
- [ ] Error paths tested (invalid input, failures, timeouts)
- [ ] Tests are deterministic (no flakiness, no time dependency)
- [ ] Tests run fast (unit tests < 1s each, integration < 5s)

### 4.2 Self-Review (act as `/review-code`)
Review your own changes against:
- [ ] **Architecture**: Does it follow the project's established patterns?
- [ ] **Correctness**: Does it handle all edge cases?
- [ ] **Security**: Input validation? Auth checks? No secrets in code?
- [ ] **Performance**: N+1 queries? Unbounded collections? Missing pagination?
- [ ] **Error handling**: Typed errors? No swallowed exceptions?
- [ ] **Naming**: Clear, intention-revealing names?

### 4.3 Security Quick Scan (act as `/security-audit`)
- [ ] All inputs validated and sanitized
- [ ] No SQL/command/template injection possible
- [ ] Auth/authz enforced on new endpoints
- [ ] No sensitive data in logs
- [ ] No hardcoded secrets

### 4.4 Run the Full Test Suite
```bash
# Run ALL tests, not just the ones you wrote
make test  # or equivalent
```

---

## Phase 5: DOCUMENT — Leave It Better Than You Found It

**Goal**: Ensure future developers (including future you) can understand the changes.

### 5.1 Code-Level Documentation
- Add comments explaining **WHY** for non-obvious logic (never what)
- Update function/method docstrings if public API changed
- Remove stale comments that no longer apply

### 5.2 Architecture Documentation
- If architectural decisions were made → create ADR (`/doc-adr`)
- If module boundaries or data flows changed → update architecture docs
- If new patterns introduced → document them

### 5.3 API Documentation
- If API changed → update OpenAPI spec
- If new endpoints → add `@extend_schema` / Swagger annotations
- If breaking change → document migration path

### 5.4 README Updates
- If setup steps changed → update README
- If new environment variables → update `.env.example`
- If new make targets or commands → update Makefile/README

### 5.5 Commit & PR
- Use conventional commit messages (`/git-commit`)
- Create a descriptive PR (`/git-pr`)

---

## Phase Summary Checklist

Before declaring the task complete, verify:

```
EXPLORE
  ✓ Understood affected modules and patterns
  ✓ Found existing code to reuse

PLAN
  ✓ Work items defined and ordered
  ✓ Interfaces designed before implementation
  ✓ Test strategy defined

IMPLEMENT (per work item)
  ✓ Test written FIRST (TDD red)
  ✓ Minimal code to pass (TDD green)
  ✓ Refactored while green (TDD refactor)
  ✓ Committed after each cycle

VERIFY
  ✓ All tests pass
  ✓ Self-reviewed for quality
  ✓ Security checked
  ✓ Full test suite passes

DOCUMENT
  ✓ Non-obvious logic commented
  ✓ ADR written (if decisions made)
  ✓ API docs updated (if API changed)
  ✓ README updated (if setup changed)
```

---

## Principles (Always Active)

- **Simplicity over cleverness** — the best code is code someone else can read in 6 months
- **Composition over inheritance** — small, composable pieces
- **Explicit over implicit** — no magic, no hidden behavior
- **Fail fast** — catch errors early, surface them clearly
- **Don't repeat yourself** — but don't abstract prematurely either (rule of three)
- **Leave it better** — Boy Scout Rule, but don't rewrite the campground
