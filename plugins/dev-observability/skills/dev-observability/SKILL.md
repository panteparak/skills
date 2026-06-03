---
name: dev-observability
description: Set up application observability with structured logging, metrics, and distributed tracing using OpenTelemetry. Use when adding monitoring, logging, or tracing to a service.
argument-hint: "[language-or-component]"
---

# Observability Setup

Set up observability for: **$ARGUMENTS**

## Three Pillars

| Pillar | What | Tool |
|--------|------|------|
| **Logs** | Discrete events with context | structlog, slog, Logback |
| **Metrics** | Numeric measurements over time | Prometheus, Micrometer |
| **Traces** | Request flow across services | OpenTelemetry, Jaeger |

## Structured Logging

### Python (structlog)
```python
import structlog

logger = structlog.get_logger()

# Good — structured with context
logger.info("order_created", order_id=order.id, customer_id=customer.id, total=order.total)

# Bad — unstructured string
logger.info(f"Created order {order.id} for customer {customer.id}")
```

Output (JSON):
```json
{"event": "order_created", "order_id": "ord-123", "customer_id": "cust-456", "total": 99.99, "timestamp": "2024-01-15T10:30:00Z", "level": "info", "correlation_id": "req-abc"}
```

### Go (slog)
```go
slog.Info("order created",
    slog.String("order_id", order.ID),
    slog.String("customer_id", order.CustomerID),
    slog.Float64("total", order.Total),
)
```

### Kotlin (Logback + structured markers)
```kotlin
logger.info("Order created", kv("orderId", order.id), kv("customerId", order.customerId))
```

### Logging Rules
- **DO log**: Business events, errors, auth events, external call results
- **DON'T log**: PII (emails, names), secrets (tokens, passwords), request/response bodies in prod
- **Always include**: correlation/request ID, timestamp, log level, service name
- **Log levels**: ERROR=actionable failure, WARN=degraded but working, INFO=business events, DEBUG=dev only

## Metrics (Prometheus)

### Key Metrics to Expose

```
# RED method — for every service endpoint
http_requests_total{method, path, status}          # Rate
http_request_duration_seconds{method, path}        # Errors & Duration

# USE method — for every resource
resource_utilization{type}                          # Utilization
resource_saturation{type}                           # Saturation
resource_errors_total{type}                         # Errors

# Business metrics
orders_created_total
orders_total_value_dollars
active_users_gauge
```

### Python (prometheus-client)
```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

# In middleware
REQUEST_COUNT.labels(method=request.method, path=request.path, status=response.status_code).inc()
REQUEST_LATENCY.labels(method=request.method, path=request.path).observe(duration)
```

### Go (prometheus/client_golang)
```go
var httpRequestsTotal = promauto.NewCounterVec(prometheus.CounterOpts{
    Name: "http_requests_total",
    Help: "Total HTTP requests",
}, []string{"method", "path", "status"})

var httpRequestDuration = promauto.NewHistogramVec(prometheus.HistogramOpts{
    Name:    "http_request_duration_seconds",
    Help:    "HTTP request latency",
    Buckets: prometheus.DefBuckets,
}, []string{"method", "path"})
```

### Spring Boot (Micrometer — auto-configured)
```yaml
# application.yml — Micrometer auto-exposes /actuator/prometheus
management:
  endpoints:
    web:
      exposure:
        include: health,prometheus,info
  metrics:
    tags:
      application: ${spring.application.name}
```

## Distributed Tracing (OpenTelemetry)

### Python (OpenTelemetry)
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# Setup
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)

# Auto-instrument frameworks
FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=engine)
HTTPXClientInstrumentor().instrument()

# Manual spans for business logic
tracer = trace.get_tracer(__name__)

async def create_order(data):
    with tracer.start_as_current_span("create_order") as span:
        span.set_attribute("order.customer_id", data.customer_id)
        span.set_attribute("order.item_count", len(data.items))
        order = await repo.save(data)
        span.set_attribute("order.id", order.id)
        return order
```

### Go (OpenTelemetry)
```go
tracer := otel.Tracer("order-service")

func (s *OrderService) CreateOrder(ctx context.Context, data CreateInput) (*Order, error) {
    ctx, span := tracer.Start(ctx, "CreateOrder")
    defer span.End()

    span.SetAttributes(
        attribute.String("customer.id", data.CustomerID),
        attribute.Int("items.count", len(data.Items)),
    )

    order, err := s.repo.Save(ctx, data)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        return nil, err
    }

    span.SetAttributes(attribute.String("order.id", order.ID))
    return order, nil
}
```

## Health Checks

Every service must expose:
- **`/health`** (liveness) — is the process alive? (simple 200 OK)
- **`/ready`** (readiness) — can the service handle traffic? (checks DB, cache, deps)

```python
# FastAPI
@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/ready")
async def ready(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "checks": {"database": "ok"}}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not ready"})
```

## Correlation IDs

Thread a unique ID through every request for cross-service tracing:

```python
# Middleware — generate or extract correlation ID
import uuid

class CorrelationIdMiddleware:
    async def __call__(self, request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
```

## Alerting Rules (Prometheus)

```yaml
groups:
  - name: service-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate above 5%"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p95 latency above 1s"
```

## Rules
- Log structured data (key-value), not formatted strings
- Never log PII, secrets, or tokens
- Expose RED metrics (Rate, Errors, Duration) for every endpoint
- Use OpenTelemetry for tracing — it's the industry standard
- Correlation IDs in every request — propagate across services
- Health checks are mandatory — `/health` and `/ready`
- Alert on symptoms (error rate, latency), not causes (CPU usage)
- Dashboards: start with RED method, add business metrics
