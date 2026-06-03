---
name: test-e2e
description: Write end-to-end tests for full user workflows using Playwright, Cypress, or API-level E2E tests. Use when testing complete user journeys.
argument-hint: "[user-flow-to-test]"
---

# End-to-End Testing

Write E2E tests for the user flow: **$ARGUMENTS**

## When to E2E Test

- Critical user journeys (signup, checkout, payment)
- Cross-service workflows
- Authentication and authorization flows
- Data flows through the entire stack

## Playwright (Web)

```typescript
import { test, expect } from "@playwright/test"

test.describe("Order Checkout Flow", () => {
  test.beforeEach(async ({ page }) => {
    // Seed test data via API
    await page.request.post("/api/test/seed", { data: { scenario: "checkout" } })
    await page.goto("/login")
    await page.fill('[name="email"]', "test@example.com")
    await page.fill('[name="password"]', "password123")
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL("/dashboard")
  })

  test("user can complete checkout", async ({ page }) => {
    // Add item to cart
    await page.goto("/products")
    await page.click('[data-testid="product-card"]:first-child button')
    await expect(page.locator('[data-testid="cart-count"]')).toHaveText("1")

    // Go to checkout
    await page.click('[data-testid="cart-icon"]')
    await page.click('text=Proceed to Checkout')

    // Fill shipping info
    await page.fill('[name="address"]', "123 Test St")
    await page.fill('[name="city"]', "Test City")
    await page.click('text=Continue to Payment')

    // Complete payment
    await page.fill('[name="cardNumber"]', "4242424242424242")
    await page.fill('[name="expiry"]', "12/25")
    await page.fill('[name="cvc"]', "123")
    await page.click('text=Place Order')

    // Verify success
    await expect(page.locator("h1")).toContainText("Order Confirmed")
    await expect(page.locator('[data-testid="order-number"]')).toBeVisible()
  })

  test("shows error on payment failure", async ({ page }) => {
    // ... add item, go to checkout
    await page.fill('[name="cardNumber"]', "4000000000000002") // Decline card
    await page.click('text=Place Order')
    await expect(page.locator('[data-testid="error-message"]')).toContainText("declined")
  })
})
```

## API-Level E2E Testing

For backend services, test the full API flow:

```python
# test_e2e_order_flow.py
@pytest.mark.e2e
class TestOrderFlow:
    def test_complete_order_lifecycle(self, api_client):
        # 1. Register user
        user = api_client.post("/api/v1/auth/register", json={...})
        token = user.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create order
        order = api_client.post("/api/v1/orders", json={
            "items": [{"product_id": "prod-1", "quantity": 2}]
        }, headers=headers)
        assert order.status_code == 201
        order_id = order.json()["id"]

        # 3. Verify order status
        detail = api_client.get(f"/api/v1/orders/{order_id}", headers=headers)
        assert detail.json()["status"] == "pending"

        # 4. Process payment (simulate webhook)
        api_client.post("/api/webhooks/payment", json={
            "order_id": order_id, "status": "paid"
        })

        # 5. Verify final state
        detail = api_client.get(f"/api/v1/orders/{order_id}", headers=headers)
        assert detail.json()["status"] == "paid"
```

## E2E Test Structure

```
tests/
├── e2e/
│   ├── fixtures/              # Test data seeding
│   │   ├── seed.ts
│   │   └── cleanup.ts
│   ├── pages/                 # Page Object Model
│   │   ├── login-page.ts
│   │   ├── checkout-page.ts
│   │   └── dashboard-page.ts
│   ├── helpers/
│   │   ├── auth.ts            # Login helper
│   │   └── api.ts             # API helpers for setup
│   └── flows/
│       ├── checkout.spec.ts
│       ├── auth.spec.ts
│       └── admin.spec.ts
├── playwright.config.ts
```

## Page Object Model

```typescript
class CheckoutPage {
  constructor(private page: Page) {}

  async fillShippingInfo(address: ShippingAddress) {
    await this.page.fill('[name="address"]', address.street)
    await this.page.fill('[name="city"]', address.city)
  }

  async submitPayment(card: CardInfo) {
    await this.page.fill('[name="cardNumber"]', card.number)
    await this.page.click('text=Place Order')
  }

  async getOrderConfirmation() {
    return this.page.locator('[data-testid="order-number"]').textContent()
  }
}
```

## Rules
- E2E tests cover critical paths only — not every feature
- Use Page Object Model for web E2E (reduces maintenance)
- Seed test data via API, not direct DB manipulation
- Clean up test data after each test
- E2E tests are slow — run in CI, not on every commit
- Use `data-testid` attributes for selectors (resilient to UI changes)
- Test the user journey, not implementation details
- Flaky tests must be fixed immediately or quarantined
