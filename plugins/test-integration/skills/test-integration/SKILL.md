---
name: test-integration
description: Write integration tests for APIs, databases, and external system boundaries using Testcontainers and real dependencies. Use when testing system boundaries.
argument-hint: "[component-to-test]"
---

# Integration Testing

Write integration tests for: **$ARGUMENTS**

## What to Integration Test

Integration tests verify **boundaries** — where your code meets external systems:
- Database queries and transactions
- REST/gRPC API endpoints
- Message queue producers/consumers
- External API clients
- File system operations
- Cache interactions

## Principles

- Use **real dependencies** (via Testcontainers), not mocks
- Test the **contract** between your code and the external system
- Test **error scenarios** from external systems (timeouts, connection failures)
- Keep tests **isolated** — each test sets up and tears down its own data

## Language-Specific Patterns

### Spring Boot (Kotlin + Testcontainers)
```kotlin
@SpringBootTest
@Testcontainers
class OrderRepositoryTest {
    companion object {
        @Container
        val postgres = PostgreSQLContainer("postgres:16-alpine")
            .withDatabaseName("test")

        @JvmStatic
        @DynamicPropertySource
        fun properties(registry: DynamicPropertyRegistry) {
            registry.add("spring.datasource.url", postgres::getJdbcUrl)
            registry.add("spring.datasource.username", postgres::getUsername)
            registry.add("spring.datasource.password", postgres::getPassword)
        }
    }

    @Autowired lateinit var repository: OrderRepository
    @Autowired lateinit var entityManager: EntityManager

    @Test
    fun `should persist and retrieve order with items`() {
        val order = OrderFixture.pendingOrder()
        repository.save(order)
        entityManager.flush()
        entityManager.clear()

        val found = repository.findById(order.id)
        assertThat(found).isPresent
        assertThat(found.get().items).hasSize(2)
    }
}

// API integration test
@SpringBootTest(webEnvironment = RANDOM_PORT)
@Testcontainers
class OrderApiTest(@Autowired val restTemplate: TestRestTemplate) {
    @Test
    fun `POST orders should create and return 201`() {
        val request = CreateOrderRequest(items = listOf(ItemRequest("prod-1", 2)))
        val response = restTemplate.postForEntity("/api/v1/orders", request, OrderResponse::class.java)
        assertThat(response.statusCode).isEqualTo(HttpStatus.CREATED)
        assertThat(response.body?.id).isNotNull()
    }
}
```

### Django (pytest-django)
```python
@pytest.mark.django_db
class TestOrderAPI:
    def test_create_order(self, authenticated_client, product_factory):
        product = product_factory(stock=10)
        response = authenticated_client.post("/api/v1/orders/", {
            "items": [{"product_id": product.id, "quantity": 2}]
        }, format="json")
        assert response.status_code == 201
        assert Order.objects.count() == 1

    def test_create_order_out_of_stock(self, authenticated_client, product_factory):
        product = product_factory(stock=0)
        response = authenticated_client.post("/api/v1/orders/", {
            "items": [{"product_id": product.id, "quantity": 1}]
        }, format="json")
        assert response.status_code == 400
        assert "out of stock" in response.data["error"]["detail"]
```

### Go (testcontainers-go)
```go
func TestOrderRepository_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }

    ctx := context.Background()
    container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: testcontainers.ContainerRequest{
            Image:        "postgres:16-alpine",
            ExposedPorts: []string{"5432/tcp"},
            Env:          map[string]string{"POSTGRES_PASSWORD": "test", "POSTGRES_DB": "test"},
            WaitingFor:   wait.ForListeningPort("5432/tcp"),
        },
        Started: true,
    })
    require.NoError(t, err)
    t.Cleanup(func() { container.Terminate(ctx) })

    dsn := fmt.Sprintf("postgres://postgres:test@%s/test?sslmode=disable", container.Endpoint(ctx, ""))
    repo := postgres.NewOrderRepository(dsn)

    t.Run("save and find", func(t *testing.T) {
        order := fixture.NewOrder()
        err := repo.Save(ctx, order)
        require.NoError(t, err)
        found, err := repo.FindByID(ctx, order.ID)
        require.NoError(t, err)
        assert.Equal(t, order.ID, found.ID)
    })
}
```

## Test Categories & Markers

Separate integration tests from unit tests:
- **Go**: `if testing.Short() { t.Skip() }` — run with `go test -short` to skip
- **Python**: `@pytest.mark.django_db` or custom `@pytest.mark.integration`
- **Kotlin**: `@Tag("integration")` with Gradle test filtering

## Database Test Patterns

- **Transaction rollback**: Wrap each test in a transaction, rollback after
- **Truncate**: Clear tables between tests (faster than recreating)
- **Fixtures/Factories**: Use factory pattern, not shared fixtures
- **Migrations**: Run real migrations against test DB

## Rules
- Use real dependencies via Testcontainers (not H2, SQLite, or in-memory fakes)
- Each test owns its data — no shared state between tests
- Test error scenarios: connection refused, timeout, constraint violation
- Integration tests can be slower — mark them separately from unit tests
- No mocking at integration level — the point is to test real interactions
- Test with production-like configuration
