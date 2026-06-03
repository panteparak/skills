---
name: dev-event-driven
description: Design and implement event-driven architecture patterns with Kafka, RabbitMQ, or cloud-native messaging. Use when building async messaging, event sourcing, or pub/sub systems.
argument-hint: "[pattern-or-feature]"
---

# Event-Driven Architecture

Implement event-driven pattern for: **$ARGUMENTS**

## When to Use Events

| Use Case | Pattern |
|----------|---------|
| Notify other services of state changes | Domain Events + Pub/Sub |
| Reliable cross-service data flow | Transactional Outbox |
| Long-running multi-step workflows | Saga (Orchestration or Choreography) |
| Rebuild state from history | Event Sourcing |
| Decouple producer from consumer | Message Queue |
| Fan-out to multiple consumers | Topic + Consumer Groups |

## Core Patterns

### 1. Domain Events

Events represent something that happened in the past. Named in past tense.

```python
# Event definition
@dataclass(frozen=True)
class OrderCreated:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    order_id: str
    customer_id: str
    total_amount: Decimal
    items: list[OrderItemData]

@dataclass(frozen=True)
class OrderShipped:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    order_id: str
    tracking_number: str
```

```go
// Go
type OrderCreated struct {
    EventID    string    `json:"event_id"`
    OccurredAt time.Time `json:"occurred_at"`
    OrderID    string    `json:"order_id"`
    CustomerID string    `json:"customer_id"`
    Total      float64   `json:"total"`
}
```

### 2. Transactional Outbox Pattern

**Problem**: How to reliably publish events when updating a database? Publishing after commit risks losing events if the app crashes. Publishing before commit risks publishing events for rolled-back transactions.

**Solution**: Write events to an outbox table within the same DB transaction. A separate process polls the outbox and publishes to the message broker.

```sql
-- Outbox table
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(255) NOT NULL,
    aggregate_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    published_at TIMESTAMP,
    retry_count INT DEFAULT 0
);

CREATE INDEX idx_outbox_unpublished ON outbox_events (created_at)
    WHERE published_at IS NULL;
```

```python
# Service — write to DB + outbox in same transaction
def create_order(customer_id: str, items: list) -> Order:
    with transaction.atomic():
        order = Order.objects.create(customer_id=customer_id, status="pending")
        OrderItem.objects.bulk_create([...])

        # Write event to outbox (same transaction!)
        OutboxEvent.objects.create(
            aggregate_type="Order",
            aggregate_id=str(order.id),
            event_type="OrderCreated",
            payload={
                "order_id": str(order.id),
                "customer_id": customer_id,
                "total": str(order.total),
            },
        )
    return order

# Outbox publisher (runs as background worker / cron)
def publish_outbox_events():
    events = OutboxEvent.objects.filter(
        published_at__isnull=True,
        retry_count__lt=5,
    ).order_by("created_at")[:100]

    for event in events:
        try:
            kafka_producer.send(
                topic=f"{event.aggregate_type}.{event.event_type}",
                value=event.payload,
                key=event.aggregate_id,
            )
            event.published_at = timezone.now()
            event.save()
        except Exception:
            event.retry_count += 1
            event.save()
```

### 3. Idempotent Consumer

**Problem**: Messages may be delivered more than once (at-least-once delivery).

**Solution**: Track processed event IDs and skip duplicates.

```python
class ProcessedEvent(models.Model):
    event_id = models.UUIDField(primary_key=True)
    processed_at = models.DateTimeField(auto_now_add=True)

def handle_order_created(event: dict):
    event_id = event["event_id"]

    # Idempotency check
    if ProcessedEvent.objects.filter(event_id=event_id).exists():
        logger.info("event_already_processed", event_id=event_id)
        return

    with transaction.atomic():
        # Process the event
        send_confirmation_email(event["customer_id"], event["order_id"])
        # Mark as processed (same transaction)
        ProcessedEvent.objects.create(event_id=event_id)
```

### 4. Saga Pattern (Orchestration)

For multi-step workflows across services with compensation on failure.

```python
class OrderSaga:
    """Orchestrates: Create Order → Reserve Stock → Process Payment → Confirm"""

    steps = [
        SagaStep(
            action=reserve_stock,
            compensation=release_stock,
        ),
        SagaStep(
            action=process_payment,
            compensation=refund_payment,
        ),
        SagaStep(
            action=confirm_order,
            compensation=cancel_order,
        ),
    ]

    def execute(self, order_data):
        completed = []
        try:
            for step in self.steps:
                step.action(order_data)
                completed.append(step)
        except Exception as e:
            # Compensate in reverse order
            for step in reversed(completed):
                try:
                    step.compensation(order_data)
                except Exception as comp_error:
                    logger.error("compensation_failed", step=step.name, error=str(comp_error))
            raise SagaFailed(f"Saga failed at step: {e}")
```

### 5. Dead Letter Queue (DLQ)

Messages that fail processing repeatedly go to a DLQ for investigation.

```python
MAX_RETRIES = 5

def consume_with_dlq(message):
    retry_count = int(message.headers.get("x-retry-count", 0))

    try:
        process_message(message)
    except Exception as e:
        if retry_count >= MAX_RETRIES:
            # Send to DLQ
            dlq_producer.send(
                topic=f"{message.topic}.dlq",
                value=message.value,
                headers={
                    "x-original-topic": message.topic,
                    "x-error": str(e),
                    "x-retry-count": str(retry_count),
                },
            )
            logger.error("message_sent_to_dlq", topic=message.topic, error=str(e))
        else:
            # Retry with backoff
            retry_producer.send(
                topic=message.topic,
                value=message.value,
                headers={"x-retry-count": str(retry_count + 1)},
            )
```

## Kafka Topic Design

```
# Naming convention: <domain>.<event-type>
orders.order-created
orders.order-shipped
payments.payment-processed
inventory.stock-reserved

# DLQ naming
orders.order-created.dlq

# Topic config for production
partitions: 6          # Match consumer count
replication-factor: 3  # For durability
retention.ms: 604800000  # 7 days
```

## Message Schema

```json
{
  "event_id": "uuid",
  "event_type": "OrderCreated",
  "occurred_at": "2024-01-15T10:30:00Z",
  "aggregate_id": "order-123",
  "aggregate_type": "Order",
  "version": 1,
  "data": {
    "order_id": "order-123",
    "customer_id": "cust-456",
    "total": 99.99
  },
  "metadata": {
    "correlation_id": "req-abc",
    "source": "order-service"
  }
}
```

## Rules
- Events are **immutable facts** — past tense, never modified after publish
- **Transactional Outbox** for reliable publishing (not publish-after-commit)
- **Idempotent consumers** — always (at-least-once delivery is the norm)
- **Dead Letter Queue** for poison messages — never lose messages silently
- **Schema versioning** — add fields (backward compatible), never remove
- **Correlation IDs** in every event — trace flows across services
- Events carry **data**, not references — consumer shouldn't need to call back
- **Order matters** — use partition keys (aggregate ID) for ordering guarantees
- **Monitor consumer lag** — alert if consumers fall behind
- **Retry with exponential backoff** — don't hammer failing consumers
