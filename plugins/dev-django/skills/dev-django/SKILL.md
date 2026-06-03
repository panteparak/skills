---
name: dev-django
description: Develop features in Django + DRF projects using services/selectors pattern, TDD, and sub-app architecture. Use when writing Django backend code.
argument-hint: "[feature-description]"
---

# Django + DRF Development

Implement the following feature using enterprise Django + DRF patterns: **$ARGUMENTS**

## Development Workflow (Strict TDD)

1. **Write failing test first** — `test_services.py` for business logic
2. **Implement service/selector** — make the test pass
3. **Write API test** — `test_api.py` for endpoint behavior
4. **Implement serializer + view** — thin API layer
5. **Refactor** — extract shared patterns

## Architecture: Services & Selectors Pattern

### Services (Write Operations)
Business logic for mutations. Called by views after serializer validation.

```python
# apps/orders/processing/services.py
from django.db import transaction

def create_order(*, customer: Customer, items: list[OrderItemData]) -> Order:
    """Create a new order with items. Raises ValidationError on failure."""
    _validate_stock(items)

    with transaction.atomic():
        order = Order.objects.create(
            customer=customer,
            status=OrderStatus.PENDING,
            total=_calculate_total(items),
        )
        OrderItem.objects.bulk_create([
            OrderItem(order=order, **item.dict()) for item in items
        ])

    notify_order_created.delay(order.id)  # Celery async
    return order
```

**Service rules:**
- Accept keyword-only arguments (`*`)
- Handle transactions explicitly
- Raise `django.core.exceptions.ValidationError` for domain errors
- Return domain objects (model instances)
- One function per use case (not a class with many methods)

### Selectors (Read Operations)
Query logic isolated from views. Returns QuerySets for composability.

```python
# apps/orders/processing/selectors.py
from django.db.models import QuerySet, Prefetch

def get_orders_for_customer(
    *, customer: Customer, status: str | None = None
) -> QuerySet[Order]:
    qs = Order.objects.filter(
        customer=customer
    ).select_related(
        "customer"
    ).prefetch_related(
        Prefetch("items", queryset=OrderItem.objects.select_related("product"))
    )
    if status:
        qs = qs.filter(status=status)
    return qs

def get_order_detail(*, order_id: int, customer: Customer) -> Order:
    return get_orders_for_customer(customer=customer).get(id=order_id)
```

**Selector rules:**
- Return `QuerySet` for lists (allows further filtering, pagination)
- Use `select_related` / `prefetch_related` to avoid N+1
- Accept keyword-only arguments
- Raise `ObjectDoesNotExist` for missing items

### DRF Views (Thin Layer)
Views validate input and delegate. No business logic.

```python
# apps/orders/processing/api/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CreateOrderSerializer, responses={201: OrderSerializer})
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = create_order(
            customer=request.user,
            items=serializer.validated_data["items"],
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OrderSerializer(many=True)})
    def get(self, request):
        orders = get_orders_for_customer(customer=request.user)
        # Pagination handled by DRF pagination class
        return self.get_paginated_response(orders)
```

### DRF Serializers (Validation + Representation)

```python
# apps/orders/processing/api/serializers.py
class CreateOrderSerializer(serializers.Serializer):
    """Input validation only — no create()/update() with business logic."""
    items = OrderItemInputSerializer(many=True, min_length=1)

class OrderSerializer(serializers.ModelSerializer):
    """Output representation."""
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Order
        fields = ["id", "status", "total", "items", "created_at"]
```

## Sub-App Communication

**Within a bounded context** (e.g., `apps/orders/`):
- Sub-apps can import from each other directly
- Shared models referenced via ForeignKey

**Across bounded contexts** (e.g., `apps/orders/` → `apps/users/`):
- Use Django signals or Celery tasks
- Never import models directly across contexts
- Use IDs, not object references

```python
# Cross-context communication via signal
from django.dispatch import Signal

order_completed = Signal()  # args: order_id, customer_id

# In the other context's apps.py
order_completed.connect(handle_order_completed)
```

## Testing Patterns

```python
# test_services.py — Unit test for business logic
class TestCreateOrder:
    def test_creates_order_with_valid_items(self, db, customer_factory, product_factory):
        customer = customer_factory()
        items = [OrderItemData(product=product_factory(), quantity=2)]
        order = create_order(customer=customer, items=items)
        assert order.status == OrderStatus.PENDING
        assert order.items.count() == 1

    def test_rejects_out_of_stock_items(self, db, customer_factory):
        customer = customer_factory()
        items = [OrderItemData(product_id=999, quantity=100)]
        with pytest.raises(ValidationError):
            create_order(customer=customer, items=items)

# test_api.py — Integration test for endpoint
class TestOrderCreateAPI:
    def test_authenticated_user_can_create_order(self, authenticated_client):
        response = authenticated_client.post("/api/v1/orders/", data={...})
        assert response.status_code == 201

    def test_anonymous_user_rejected(self, api_client):
        response = api_client.post("/api/v1/orders/", data={...})
        assert response.status_code == 401
```

## Rules
- Business logic in `services.py` / `selectors.py` ONLY
- Views are thin — validate, delegate, respond
- Serializers validate input and format output — no business logic
- No `create()` / `update()` overrides in serializers with domain logic
- Use keyword-only arguments (`*`) in services and selectors
- Avoid N+1: always use `select_related` / `prefetch_related` in selectors
- Type hints everywhere (Python 3.12+ syntax: `list[str]`, `str | None`)
- Each sub-app has its own `tests/` + `factories.py`
- Use `ruff` for linting, `mypy` for type checking
