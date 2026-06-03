---
name: test-generate
description: Generate comprehensive test cases and test suites for existing code. Analyzes code to produce unit, edge case, and error path tests. Use when you need tests for existing code.
argument-hint: "[file-or-function-to-test]"
---

# Generate Test Cases

Generate comprehensive tests for: **$ARGUMENTS**

## Process

1. **Read the source code** thoroughly
2. **Identify the testing framework** used in the project (check existing tests, config files)
3. **Map all code paths** — branches, loops, error returns, early exits
4. **Generate test matrix** using the categories below
5. **Write tests** matching project conventions
6. **Verify tests compile/run**

## Test Matrix Template

For each function/method, generate tests in ALL categories:

### Category 1: Happy Path (Normal Operations)
- Standard valid input → expected output
- Multiple valid combinations
- Verify return values AND side effects

### Category 2: Boundary Values
- Minimum valid input (0, 1, empty string "")
- Maximum valid input (MAX_INT, very long strings)
- Just inside valid range
- Just outside valid range (off-by-one)

### Category 3: Edge Cases
- Empty collections ([], {}, "")
- Single element collections
- Nil/null/None/undefined inputs (if applicable)
- Duplicate values
- Unicode and special characters
- Very large inputs
- Concurrent access (if threaded)
- Whitespace variations

### Category 4: Error Paths
- Invalid input types
- Missing required fields
- Constraint violations
- External dependency failures (if mocked)
- Permission/authorization failures

### Category 5: State Transitions (for stateful code)
- Valid transitions (A → B → C)
- Invalid transitions (A → C skipping B)
- Idempotent operations (calling twice = same result)
- Concurrent state modifications

### Category 6: Integration Points (if the code calls external systems)
- Successful response
- Error response (4xx, 5xx)
- Timeout
- Malformed response
- Connection refused

## Output Format

Generate tests in this order:
1. Happy path tests first
2. Edge cases grouped logically
3. Error path tests
4. Add descriptive test names that explain the scenario

## Example Output

```
Generated 15 test cases for `OrderService.createOrder()`:

Happy Path (3):
  ✓ creates order with single item
  ✓ creates order with multiple items
  ✓ applies discount code correctly

Boundary (3):
  ✓ handles maximum item quantity (9999)
  ✓ handles minimum item quantity (1)
  ✓ handles order with maximum items (100)

Edge Cases (4):
  ✓ handles duplicate product IDs by merging quantities
  ✓ handles unicode product names
  ✓ handles zero-priced items (free samples)
  ✓ is idempotent with same idempotency key

Error Paths (5):
  ✓ rejects empty items list
  ✓ rejects negative quantity
  ✓ rejects non-existent product ID
  ✓ rejects when customer not found
  ✓ handles database connection failure
```

## Rules
- Match the project's existing test style and framework
- Use the project's existing test utilities and factories
- Generate descriptive test names (behavior, not implementation)
- Include setup/teardown when needed
- Aim for high branch coverage
- Don't test private/internal methods directly
- Don't test framework/library code
- Each test should be independent and runnable alone
