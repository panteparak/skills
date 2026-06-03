---
name: dev-maintain
description: Audit and improve code maintainability — SOLID principles, coupling analysis, complexity reduction, dependency health, and tech debt management. Use when assessing or improving code quality and maintainability.
argument-hint: "[module-or-file-to-audit]"
---

# Code Maintainability Audit & Improvement

Audit and improve maintainability of: **$ARGUMENTS**

---

## Phase 1: Maintainability Assessment

### 1.1 SOLID Principles Check

#### S — Single Responsibility
```
For each class/module:
- Does it have ONE reason to change?
- Can you describe its purpose in one sentence WITHOUT "and"?

🚩 Violation signs:
  - Class name includes "And", "Manager", "Handler", "Processor", "Utils"
  - File > 300 lines
  - Class has methods that don't use the same instance variables
  - Change in one feature requires editing this class
```

#### O — Open/Closed
```
- Can you extend behavior WITHOUT modifying existing code?
- Are there long if/else or switch chains that grow with new features?

🚩 Violation signs:
  - Adding a new type requires modifying existing switch/if chains
  - New features always require editing core classes

✅ Fix: Strategy pattern, polymorphism, plugin architecture
```

#### L — Liskov Substitution
```
- Can subclasses be used wherever the parent is expected?
- Do overrides change the behavior contract?

🚩 Violation signs:
  - Subclass throws exceptions the parent doesn't
  - Subclass ignores parent methods (empty overrides)
  - Type checking in consumer code (isinstance, typeof)
```

#### I — Interface Segregation
```
- Are interfaces focused and cohesive?
- Are consumers forced to depend on methods they don't use?

🚩 Violation signs:
  - Interface with > 5 methods
  - Implementors that raise NotImplemented for some methods
  - "God interfaces" that every class must implement

✅ Fix: Split into focused interfaces
```

#### D — Dependency Inversion
```
- Do high-level modules depend on abstractions, not concrete implementations?
- Is the domain layer free of infrastructure imports?

🚩 Violation signs:
  - Service imports a specific DB driver directly
  - Domain entity imports an ORM annotation
  - Business logic creates its own dependencies (new Database())

✅ Fix: Define interfaces in domain, implement in infrastructure, inject via constructor
```

### 1.2 Coupling Analysis

```
For each module, measure:

AFFERENT COUPLING (Ca) — Who depends on ME?
  High Ca = many dependents = hard to change (careful!)

EFFERENT COUPLING (Ce) — Who do I depend on?
  High Ce = many dependencies = fragile, affected by others' changes

INSTABILITY = Ce / (Ca + Ce)
  0 = stable (many depend on it, be careful changing)
  1 = unstable (depends on many, easy to change)

RULE: Depend in the direction of stability.
  Unstable modules should depend on stable ones, not the other way around.
```

#### Coupling Red Flags
- [ ] Feature module imports from another feature module directly
- [ ] Domain layer imports infrastructure/framework code
- [ ] Circular dependencies between modules
- [ ] God module that everything depends on (high Ca AND high Ce)
- [ ] Shared mutable state between modules
- [ ] Passing framework-specific types across module boundaries

### 1.3 Complexity Analysis

```
For each function/method, assess:

CYCLOMATIC COMPLEXITY — Number of independent paths through code
  1-5:  Simple ✅
  6-10: Moderate (consider splitting)
  11+:  Complex 🚩 (must refactor)

COGNITIVE COMPLEXITY — How hard is it for a human to understand?
  Check for:
  - Deep nesting (> 3 levels)
  - Multiple return paths
  - Boolean logic complexity
  - Implicit state changes
```

#### Complexity Red Flags
- [ ] Functions > 30 lines
- [ ] Nesting > 3 levels deep
- [ ] Functions with > 5 parameters
- [ ] Methods that are hard to name (do too many things)
- [ ] Boolean parameters that change behavior (flag arguments)
- [ ] Functions where you need to scroll to see the whole thing

### 1.4 Naming Quality Audit

```
Good names tell you:
  WHAT it is (not how it works)
  WHY it exists (not what it contains)

Bad naming patterns:
  ❌ data, info, item, obj, result, temp, val
  ❌ processData(), handleStuff(), doWork()
  ❌ isFlag, flag, status (without context)
  ❌ Abbreviations: usr, msg, btn, impl

Good naming patterns:
  ✅ unpaidOrders, customerEmail, shippingAddress
  ✅ calculateOrderTotal(), sendConfirmationEmail()
  ✅ isEligibleForDiscount, hasExceededRateLimit
  ✅ OrderRepository, PaymentGateway, EmailNotifier
```

---

## Phase 2: Dependency Health

### 2.1 Dependency Audit
```
For each external dependency:
- Is it still maintained? (last release, open issues)
- Is it used for more than one thing? (justified dependency)
- Are there security vulnerabilities? (CVE check)
- Could it be replaced with stdlib? (reduce dep count)
- Is the version pinned? (reproducible builds)
```

### 2.2 Dependency Direction Validation
```
ALLOWED dependency direction:
  transport → application → domain
  infrastructure → domain (implements interfaces)

FORBIDDEN:
  domain → infrastructure ❌
  domain → transport ❌
  feature A → feature B ❌ (use events/signals instead)
```

### 2.3 Framework Coupling
```
How hard would it be to swap the framework?
  - Domain logic: ZERO framework imports (pure language)
  - Application logic: minimal framework (DI, transactions)
  - Infrastructure: framework-coupled (OK, expected)
  - Transport: framework-coupled (OK, expected)

If domain imports framework code → extract and decouple
```

---

## Phase 3: Tech Debt Inventory

### 3.1 Debt Classification

| Type | Description | Example |
|------|-------------|---------|
| **Design debt** | Architecture shortcuts | God class, missing abstraction |
| **Code debt** | Poor code quality | Duplication, complexity, naming |
| **Test debt** | Missing/poor tests | No edge case tests, flaky tests |
| **Doc debt** | Missing/stale docs | Outdated README, no ADRs |
| **Dependency debt** | Outdated/vulnerable deps | Unpinned versions, old libraries |
| **Infrastructure debt** | Manual processes | No CI, manual deploys |

### 3.2 Debt Prioritization Matrix

```
               HIGH IMPACT
                    │
     ┌──────────────┼──────────────┐
     │              │              │
     │   DO NEXT    │   DO NOW     │
     │  (schedule)  │  (critical)  │
     │              │              │
LOW ─┼──────────────┼──────────────┼─ HIGH
EFFORT│              │              │ EFFORT
     │   DO LATER   │   DISCUSS    │
     │  (backlog)   │  (worth it?) │
     │              │              │
     └──────────────┼──────────────┘
                    │
               LOW IMPACT
```

### 3.3 Debt Tracking Template

```markdown
## Tech Debt Register

| ID | Type | Description | Module | Impact | Effort | Priority | Status |
|----|------|-------------|--------|--------|--------|----------|--------|
| TD-001 | Design | OrderService has 15 methods | orders | High | Medium | P1 | Open |
| TD-002 | Test | No integration tests for payment | payments | High | Low | P0 | Open |
| TD-003 | Code | Duplicate validation logic | auth, users | Medium | Low | P1 | Open |
```

---

## Phase 4: Improvement Actions

Based on the audit, generate prioritized improvement actions:

### Quick Wins (< 1 hour each)
- Rename unclear variables/functions
- Extract magic numbers to named constants
- Remove dead code and unused imports
- Add missing type hints
- Fix obvious code smells

### Short-Term (1 sprint)
- Extract large classes into focused ones
- Replace if/else chains with polymorphism
- Add missing test coverage for critical paths
- Update stale documentation
- Fix dependency direction violations

### Long-Term (plan across sprints)
- Refactor god modules using Strangler Fig pattern
- Introduce missing abstractions (repository pattern, etc.)
- Migrate from deprecated dependencies
- Add comprehensive observability
- Introduce contract tests between modules

---

## Maintainability Report Template

```markdown
# Maintainability Report: [Module/Project]

**Date**: YYYY-MM-DD
**Score**: X/10

## Summary
[2-3 sentence overview of maintainability state]

## SOLID Violations
| Principle | Location | Severity | Fix |
|-----------|----------|----------|-----|
| SRP | OrderService | High | Split into OrderCreator, OrderCanceller |

## Coupling Issues
| Issue | Modules | Severity |
|-------|---------|----------|
| Circular dep | orders ↔ inventory | High |

## Complexity Hotspots
| File:Function | Complexity | Lines | Recommendation |
|---------------|-----------|-------|----------------|
| order_service.py:process | 15 | 85 | Extract methods |

## Tech Debt
[Reference tech debt register]

## Recommended Actions (Prioritized)
1. **[P0]** [action] — [why, effort estimate]
2. **[P1]** [action] — [why, effort estimate]
3. **[P2]** [action] — [why, effort estimate]
```

---

## Rules
- Audit BEFORE refactoring — understand what's wrong before fixing
- Fix the highest-impact issues first
- Each refactoring must have tests BEFORE you start
- Small, incremental improvements > big-bang rewrites
- Track tech debt explicitly — hidden debt compounds
- Dependency direction is non-negotiable: domain must be pure
- Naming is not bikeshedding — unclear names cause bugs
- Complexity kills maintainability — if you can't explain a function in one sentence, split it
