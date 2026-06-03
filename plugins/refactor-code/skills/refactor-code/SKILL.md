---
name: refactor-code
description: Systematically refactor code using proven patterns while maintaining behavior. Use when improving code structure, reducing complexity, or paying down tech debt.
argument-hint: "[file-or-component-to-refactor]"
---

# Systematic Refactoring

Refactor the following code: **$ARGUMENTS**

## Process (Safety First)

1. **Ensure test coverage exists** — if not, write characterization tests FIRST
2. **Identify the smell** — what exactly makes this code problematic?
3. **Choose a refactoring pattern** — from the catalog below
4. **Apply in small steps** — each step keeps tests green
5. **Verify behavior preserved** — run tests after every change

## Code Smell Detection

### Smell Catalog & Fixes

| Smell | Symptoms | Refactoring |
|-------|----------|-------------|
| **Long Method** | >20 lines, multiple levels of abstraction | Extract Method |
| **Large Class** | >300 lines, multiple responsibilities | Extract Class, Move Method |
| **Feature Envy** | Method uses another class's data more than its own | Move Method |
| **Data Clump** | Same group of params passed together | Extract Parameter Object |
| **Primitive Obsession** | Using strings/ints for domain concepts | Replace with Value Object |
| **Switch/If Chains** | Long if/else or switch on type | Replace with Polymorphism |
| **Shotgun Surgery** | One change requires editing many files | Move Method, Inline Class |
| **Divergent Change** | One class changed for many different reasons | Extract Class per reason |
| **God Object** | One class does everything | Break into focused classes |
| **Deep Nesting** | >3 levels of indentation | Extract Method, Guard Clauses |
| **Dead Code** | Unused methods, variables, imports | Delete it |
| **Duplicate Code** | Same logic in multiple places | Extract Method/Module |

## Refactoring Patterns

### Extract Method
```
# Before
def process_order(order):
    # validate
    if not order.items:
        raise ValueError("Empty order")
    if order.total < 0:
        raise ValueError("Invalid total")
    # calculate
    subtotal = sum(item.price * item.qty for item in order.items)
    tax = subtotal * 0.1
    total = subtotal + tax
    # save
    db.save(order)
    notify(order.customer)

# After
def process_order(order):
    validate_order(order)
    total = calculate_total(order)
    finalize_order(order, total)
```

### Replace Conditional with Polymorphism
```
# Before
def calculate_shipping(order):
    if order.type == "standard":
        return order.weight * 5
    elif order.type == "express":
        return order.weight * 10 + 15
    elif order.type == "overnight":
        return order.weight * 20 + 30

# After
class ShippingStrategy(Protocol):
    def calculate(self, weight: float) -> float: ...

class StandardShipping:
    def calculate(self, weight: float) -> float:
        return weight * 5

class ExpressShipping:
    def calculate(self, weight: float) -> float:
        return weight * 10 + 15

STRATEGIES = {"standard": StandardShipping(), "express": ExpressShipping(), ...}
```

### Guard Clauses (Reduce Nesting)
```
# Before
def get_payment(order):
    if order:
        if order.is_paid:
            if order.payment:
                return order.payment
            else:
                raise Error("No payment record")
        else:
            raise Error("Unpaid")
    else:
        raise Error("No order")

# After
def get_payment(order):
    if not order:
        raise Error("No order")
    if not order.is_paid:
        raise Error("Unpaid")
    if not order.payment:
        raise Error("No payment record")
    return order.payment
```

### Introduce Parameter Object
```
# Before — data clump passed everywhere
def create_report(start_date, end_date, timezone, format, include_header):
    ...
def export_report(start_date, end_date, timezone, format, include_header):
    ...

# After — cohesive parameter object
@dataclass
class ReportConfig:
    start_date: date
    end_date: date
    timezone: str = "UTC"
    format: str = "pdf"
    include_header: bool = True

def create_report(config: ReportConfig): ...
def export_report(config: ReportConfig): ...
```

## Large-Scale Refactoring Strategies

### Strangler Fig Pattern
For replacing legacy code without big-bang rewrites:
1. Identify a boundary (API endpoint, module interface)
2. Build new implementation behind the same interface
3. Route traffic to new implementation gradually
4. Remove old code when fully migrated

### Parallel Change (Expand-Contract)
For changing interfaces safely:
1. **Expand**: Add new interface alongside old one
2. **Migrate**: Update all callers to use new interface
3. **Contract**: Remove old interface

### Branch by Abstraction
For replacing a dependency:
1. Introduce an abstraction (interface) over the current dependency
2. Update all usages to go through the abstraction
3. Create new implementation behind the abstraction
4. Switch to new implementation
5. Remove old implementation

## Refactoring Workflow

```
1. Run tests → all green? (if not, fix tests first)
2. Identify ONE smell to fix
3. Apply ONE refactoring step
4. Run tests → still green?
   → Yes: commit, go to step 2
   → No: revert, try smaller step
5. Repeat until clean
```

## Rules
- **Never refactor without tests** — write characterization tests if none exist
- **One refactoring at a time** — don't combine with feature work
- **Each step must keep tests green** — if tests break, revert and try a smaller step
- **No behavior changes** — if behavior changes, that's a feature, not a refactoring
- **Commit after each successful step** — small, atomic commits
- **Don't refactor everything** — fix what hurts, leave what works
- **Boy Scout Rule** — leave code better than you found it, but don't rewrite the campground
