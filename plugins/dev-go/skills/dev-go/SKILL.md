---
name: dev-go
description: Develop features in Go services using clean architecture, TDD, and idiomatic Go patterns. Use when writing Go backend code.
argument-hint: "[feature-description]"
---

# Go Service Development

Implement the following feature using idiomatic Go patterns: **$ARGUMENTS**

## Development Workflow (Strict TDD)

1. **Write failing test first** — table-driven test for domain logic
2. **Implement minimal code** — make the test pass
3. **Write integration test** — for repository/handler layer
4. **Implement infrastructure** — DB repository, HTTP handler
5. **Refactor** — extract interfaces, simplify

## Architecture Layers

### Domain Layer (`internal/domain/<entity>/`)
Pure business logic. No external dependencies.

```go
// internal/domain/order/entity.go
package order

type Order struct {
    ID        OrderID
    Customer  CustomerID
    Items     []Item
    Status    Status
    CreatedAt time.Time
}

func (o *Order) TotalAmount() Money {
    var total Money
    for _, item := range o.Items {
        total = total.Add(item.Subtotal())
    }
    return total
}

func (o *Order) Cancel() error {
    if o.Status != StatusPending && o.Status != StatusConfirmed {
        return ErrInvalidStatusTransition{From: o.Status, To: StatusCancelled}
    }
    o.Status = StatusCancelled
    return nil
}
```

```go
// internal/domain/order/repository.go — Port (interface)
package order

type Repository interface {
    Save(ctx context.Context, order *Order) error
    FindByID(ctx context.Context, id OrderID) (*Order, error)
    FindByCustomer(ctx context.Context, customerID CustomerID, opts ListOptions) ([]Order, error)
}
```

```go
// internal/domain/order/errors.go
package order

var (
    ErrNotFound = errors.New("order not found")
)

type ErrInvalidStatusTransition struct {
    From, To Status
}

func (e ErrInvalidStatusTransition) Error() string {
    return fmt.Sprintf("cannot transition from %s to %s", e.From, e.To)
}
```

### Application Layer (`internal/application/<feature>/`)
Orchestrates domain objects. Defines use cases.

```go
// internal/application/order/handler.go
package order

type CreateHandler struct {
    repo   domain.Repository
    events event.Publisher
    log    *slog.Logger
}

func NewCreateHandler(repo domain.Repository, events event.Publisher, log *slog.Logger) *CreateHandler {
    return &CreateHandler{repo: repo, events: events, log: log}
}

type CreateInput struct {
    CustomerID string
    Items      []ItemInput
}

func (h *CreateHandler) Handle(ctx context.Context, input CreateInput) (*domain.Order, error) {
    order, err := domain.NewOrder(input.CustomerID, input.Items)
    if err != nil {
        return nil, fmt.Errorf("creating order: %w", err)
    }
    if err := h.repo.Save(ctx, order); err != nil {
        return nil, fmt.Errorf("saving order: %w", err)
    }
    h.events.Publish(ctx, domain.OrderCreated{OrderID: order.ID})
    return order, nil
}
```

### Infrastructure Layer (`internal/infrastructure/`)
Implements domain interfaces.

```go
// internal/infrastructure/postgres/order_repo.go
type OrderRepository struct {
    db *pgxpool.Pool
}

func (r *OrderRepository) Save(ctx context.Context, order *domain.Order) error {
    query := `INSERT INTO orders (id, customer_id, status, created_at)
              VALUES ($1, $2, $3, $4)
              ON CONFLICT (id) DO UPDATE SET status = $3`
    _, err := r.db.Exec(ctx, query, order.ID, order.Customer, order.Status, order.CreatedAt)
    return err
}
```

### Transport Layer (`internal/transport/http/`)
HTTP handlers. Thin — parse request, call handler, write response.

```go
func (s *Server) handleCreateOrder() http.HandlerFunc {
    type request struct {
        CustomerID string      `json:"customer_id" validate:"required"`
        Items      []ItemInput `json:"items" validate:"required,min=1,dive"`
    }
    return func(w http.ResponseWriter, r *http.Request) {
        var req request
        if err := s.decode(r, &req); err != nil {
            s.respondError(w, r, err)
            return
        }
        order, err := s.createOrder.Handle(r.Context(), order.CreateInput(req))
        if err != nil {
            s.respondError(w, r, err)
            return
        }
        s.respond(w, r, http.StatusCreated, toOrderResponse(order))
    }
}
```

## Testing Patterns

### Table-Driven Tests
```go
func TestOrder_Cancel(t *testing.T) {
    tests := []struct {
        name    string
        status  Status
        wantErr bool
    }{
        {"pending order can be cancelled", StatusPending, false},
        {"confirmed order can be cancelled", StatusConfirmed, false},
        {"shipped order cannot be cancelled", StatusShipped, true},
        {"delivered order cannot be cancelled", StatusDelivered, true},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            order := &Order{Status: tt.status}
            err := order.Cancel()
            if tt.wantErr {
                assert.Error(t, err)
            } else {
                assert.NoError(t, err)
                assert.Equal(t, StatusCancelled, order.Status)
            }
        })
    }
}
```

### Integration Tests with Testcontainers
```go
func TestOrderRepository_Save(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }
    ctx := context.Background()
    db := testutil.NewPostgresContainer(t) // helper using testcontainers-go
    repo := postgres.NewOrderRepository(db)

    order := fixture.NewOrder()
    err := repo.Save(ctx, order)
    require.NoError(t, err)

    found, err := repo.FindByID(ctx, order.ID)
    require.NoError(t, err)
    assert.Equal(t, order.ID, found.ID)
}
```

## Error Handling

```go
// Wrap errors with context
if err != nil {
    return fmt.Errorf("fetching order %s: %w", id, err)
}

// Check specific errors
if errors.Is(err, order.ErrNotFound) {
    s.respond(w, r, http.StatusNotFound, errorResponse("order not found"))
    return
}

// Custom error types for domain errors
var transitionErr *order.ErrInvalidStatusTransition
if errors.As(err, &transitionErr) {
    s.respond(w, r, http.StatusConflict, errorResponse(transitionErr.Error()))
    return
}
```

## Rules
- Accept interfaces, return structs
- `internal/domain/` has ZERO external dependencies
- Table-driven tests for all domain logic
- Errors are values — wrap with `fmt.Errorf("...: %w", err)`
- No `init()` — explicit dependency injection in `main.go`
- Use `context.Context` as first parameter
- Use `log/slog` for structured logging (Go 1.21+)
- Prefer stdlib when possible (`net/http`, `encoding/json`, `log/slog`)
- No global state or package-level variables
- `go vet`, `golangci-lint` must pass
