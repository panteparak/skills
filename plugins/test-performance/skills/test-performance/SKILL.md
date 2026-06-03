---
name: test-performance
description: Write load and performance tests using k6 or Locust to validate throughput, latency, and reliability under load. Use when testing application performance.
argument-hint: "[endpoint-or-scenario]"
---

# Performance Testing

Write performance tests for: **$ARGUMENTS**

## Process

1. **Define SLOs** — what are the targets? (p99 latency, throughput, error rate)
2. **Choose tool** — k6 (scripted, CI-friendly) or Locust (Python, interactive)
3. **Design scenarios** — smoke, load, stress, spike, soak
4. **Write tests** — realistic user flows with think time
5. **Run and analyze** — identify bottlenecks
6. **Set thresholds** — fail CI if SLOs breached

## Test Types

| Type | Purpose | Users | Duration |
|------|---------|-------|----------|
| **Smoke** | Verify system works | 1-5 | 1 min |
| **Load** | Normal expected traffic | Target RPS | 10-30 min |
| **Stress** | Find breaking point | Ramp beyond target | 20-40 min |
| **Spike** | Sudden traffic burst | 0 → max → 0 | 5-10 min |
| **Soak** | Find memory leaks, degradation | Target RPS | 1-4 hours |

## k6 (Recommended for CI)

### Basic Load Test
```javascript
// tests/performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const orderLatency = new Trend('order_creation_latency');

export const options = {
  // SLO thresholds — test FAILS if breached
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // 95th < 500ms, 99th < 1s
    errors: ['rate<0.01'],                             // Error rate < 1%
    order_creation_latency: ['p(95)<800'],
  },

  // Load profile
  stages: [
    { duration: '2m', target: 50 },    // Ramp up to 50 users
    { duration: '5m', target: 50 },    // Hold at 50 users
    { duration: '2m', target: 100 },   // Ramp up to 100
    { duration: '5m', target: 100 },   // Hold at 100
    { duration: '2m', target: 0 },     // Ramp down
  ],
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export function setup() {
  // Login and get token
  const res = http.post(`${BASE_URL}/api/v1/auth/login`, JSON.stringify({
    email: 'loadtest@example.com',
    password: 'testpassword',
  }), { headers: { 'Content-Type': 'application/json' } });

  return { token: res.json('token') };
}

export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${data.token}`,
  };

  // Scenario: Browse → Add to Cart → Checkout
  // 1. List products
  const products = http.get(`${BASE_URL}/api/v1/products?page=1`, { headers });
  check(products, {
    'products: status 200': (r) => r.status === 200,
    'products: has data': (r) => r.json('data').length > 0,
  }) || errorRate.add(1);

  sleep(1); // Think time — simulates real user behavior

  // 2. Create order
  const start = Date.now();
  const order = http.post(`${BASE_URL}/api/v1/orders`, JSON.stringify({
    items: [{ product_id: 'prod-1', quantity: 1 }],
  }), { headers });
  orderLatency.add(Date.now() - start);

  check(order, {
    'order: status 201': (r) => r.status === 201,
    'order: has id': (r) => r.json('id') !== undefined,
  }) || errorRate.add(1);

  sleep(2); // Think time
}
```

### Stress Test
```javascript
export const options = {
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // More lenient under stress
  },
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 200 },
    { duration: '5m', target: 500 },    // Beyond expected capacity
    { duration: '5m', target: 1000 },   // Find breaking point
    { duration: '5m', target: 0 },
  ],
};
```

### Spike Test
```javascript
export const options = {
  stages: [
    { duration: '1m', target: 10 },     // Normal
    { duration: '10s', target: 500 },    // Sudden spike
    { duration: '3m', target: 500 },     // Hold spike
    { duration: '10s', target: 10 },     // Drop back
    { duration: '3m', target: 10 },      // Recovery
    { duration: '1m', target: 0 },
  ],
};
```

## Locust (Python Alternative)

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class OrderUser(HttpUser):
    wait_time = between(1, 3)  # Think time: 1-3 seconds

    def on_start(self):
        """Login on user start."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "loadtest@example.com",
            "password": "testpassword",
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)  # Weight: 3x more likely than other tasks
    def list_products(self):
        self.client.get("/api/v1/products", headers=self.headers)

    @task(1)
    def create_order(self):
        self.client.post("/api/v1/orders", json={
            "items": [{"product_id": "prod-1", "quantity": 1}]
        }, headers=self.headers)
```

Run: `uv run locust -f tests/performance/locustfile.py --host http://localhost:8000`

## Running in CI

### k6 in GitHub Actions
```yaml
  performance:
    runs-on: ubuntu-latest
    needs: deploy-staging
    steps:
      - uses: actions/checkout@v4
      - uses: grafana/k6-action@v0.3.1
        with:
          filename: tests/performance/load-test.js
        env:
          BASE_URL: https://staging.example.com
```

## What to Measure

| Metric | SLO Example | How |
|--------|-------------|-----|
| **p95 latency** | < 500ms | `http_req_duration p(95)<500` |
| **p99 latency** | < 1s | `http_req_duration p(99)<1000` |
| **Throughput** | > 100 RPS | Check k6 summary output |
| **Error rate** | < 1% | `errors rate<0.01` |
| **Availability** | 99.9% | Derived from error rate |

## Rules
- Always include **think time** (`sleep()`) — otherwise you test raw throughput, not user behavior
- Set **thresholds** that fail the test — don't just collect data
- Test against **staging** with production-like data, never production
- Run **smoke test** first to validate the script works
- Include **authentication** in test flow (realistic token handling)
- Monitor **server-side metrics** during test (CPU, memory, DB connections, queue depth)
- **Ramp up gradually** — sudden full load isn't realistic and hides issues
- Store results for **trend analysis** — compare across releases
