---
name: test-unit
description: Write unit tests following TDD with proper patterns for any language. Use when you need to write or improve unit tests.
argument-hint: "[file-or-function-to-test]"
---

# Unit Testing (TDD)

Write unit tests for: **$ARGUMENTS**

## Workflow

1. **Read the source code** — understand the function/class behavior
2. **Identify test cases** — happy path, edge cases, error paths
3. **Write tests FIRST** (if TDD) or alongside code
4. **Run tests** — verify they pass (or fail if TDD)
5. **Refactor** — improve test clarity

## Test Case Discovery Checklist

For every function/method, consider:

### Happy Path
- Normal input → expected output
- Multiple valid inputs
- Boundary values (min, max of valid range)

### Edge Cases
- Empty input (empty string, empty list, null/nil/None)
- Single element
- Maximum size / large input
- Unicode / special characters
- Zero, negative numbers
- Boundary values (off-by-one)
- Whitespace-only strings

### Error Paths
- Invalid input types
- Missing required fields
- Out-of-range values
- Null/nil/None where not expected
- Concurrent access (if applicable)
- Network/IO failures (for code with external deps)

### State
- Before/after state changes
- Idempotency (calling twice = same result)
- Order dependency (if any)

## Language-Specific Patterns

### Kotlin (JUnit 5 + AssertJ)
```kotlin
@Test
fun `should calculate total for order with multiple items`() {
    val order = Order(items = listOf(
        Item(price = Money(10.0), quantity = 2),
        Item(price = Money(5.0), quantity = 1),
    ))
    assertThat(order.totalAmount()).isEqualTo(Money(25.0))
}

@ParameterizedTest
@CsvSource("1,1", "2,2", "10,55")
fun `fibonacci should return correct values`(n: Int, expected: Int) {
    assertThat(fibonacci(n)).isEqualTo(expected)
}
```

### Python (pytest)
```python
class TestCreateOrder:
    def test_valid_order(self):
        order = create_order(customer=customer, items=[item])
        assert order.status == "pending"

    @pytest.mark.parametrize("quantity,expected", [(0, False), (1, True), (100, True)])
    def test_validates_quantity(self, quantity, expected):
        assert is_valid_quantity(quantity) == expected

    def test_raises_on_empty_items(self):
        with pytest.raises(ValidationError, match="at least one item"):
            create_order(customer=customer, items=[])
```

### Go (table-driven)
```go
func TestCalculateDiscount(t *testing.T) {
    tests := []struct {
        name     string
        amount   float64
        tier     string
        expected float64
    }{
        {"no discount for basic", 100.0, "basic", 0.0},
        {"10% for premium", 100.0, "premium", 10.0},
        {"zero amount", 0.0, "premium", 0.0},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := CalculateDiscount(tt.amount, tt.tier)
            assert.Equal(t, tt.expected, got)
        })
    }
}
```

### TypeScript (Vitest)
```typescript
describe("calculateTotal", () => {
  it("should sum item prices with quantities", () => {
    const items = [
      { price: 10, quantity: 2 },
      { price: 5, quantity: 1 },
    ]
    expect(calculateTotal(items)).toBe(25)
  })

  it.each([
    { input: [], expected: 0 },
    { input: [{ price: 0, quantity: 1 }], expected: 0 },
  ])("should handle edge case: $input", ({ input, expected }) => {
    expect(calculateTotal(input)).toBe(expected)
  })
})
```

## Rules
- One assertion per test (or closely related assertions)
- Test names describe behavior, not implementation
- No test interdependency — each test runs in isolation
- No mocking of the unit under test
- Mock only direct dependencies (not transitive)
- Tests must be deterministic — no randomness, no time dependency
- Follow Arrange-Act-Assert (AAA) pattern
- Test public API, not private internals
- If a test is hard to write, the code may need refactoring
