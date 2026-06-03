---
name: dev-springboot
description: Develop features in Spring Boot + Kotlin projects using TDD, clean architecture, and enterprise patterns. Use when writing Spring Boot backend code.
argument-hint: "[feature-description]"
---

# Spring Boot + Kotlin Development

Implement the following feature using enterprise Spring Boot + Kotlin patterns: **$ARGUMENTS**

## Development Workflow (Strict TDD)

1. **Write failing test first** — unit test for domain logic
2. **Implement minimal code** — make the test pass
3. **Refactor** — clean up while tests stay green
4. **Write integration test** — for persistence/API layer
5. **Implement infrastructure** — repository, controller

## Architecture Layers

### Domain Layer (`domain/`)
- **Entities**: Rich domain objects with behavior, use Kotlin `data class` for value objects
- **Repository interfaces**: Ports — domain defines the contract, infrastructure implements
- **Domain services**: Business rules that don't belong to a single entity
- **Domain events**: For cross-feature communication

```kotlin
// Entity with behavior, not anemic
data class Order(
    val id: OrderId,
    val items: List<OrderItem>,
    val status: OrderStatus,
) {
    fun totalAmount(): Money = items.sumOf { it.subtotal() }
    fun canBeCancelled(): Boolean = status in listOf(OrderStatus.PENDING, OrderStatus.CONFIRMED)
    fun cancel(): Order {
        check(canBeCancelled()) { "Order $id cannot be cancelled in status $status" }
        return copy(status = OrderStatus.CANCELLED)
    }
}
```

### Application Layer (`application/`)
- **Use case services**: Orchestrate domain objects, enforce transactions
- **DTOs**: Request/response objects — never expose domain entities to API
- **Mappers**: Convert between domain and DTO (use extension functions)

```kotlin
@Service
@Transactional
class CreateOrderUseCase(
    private val orderRepository: OrderRepository,
    private val eventPublisher: DomainEventPublisher,
) {
    fun execute(request: CreateOrderRequest): OrderResponse {
        val order = Order.create(request.toDomain())
        val saved = orderRepository.save(order)
        eventPublisher.publish(OrderCreatedEvent(saved.id))
        return saved.toResponse()
    }
}
```

### Infrastructure Layer (`infrastructure/`)
- **JPA repositories**: Implement domain repository interfaces
- **JPA entities**: Separate from domain entities, with `@Entity` annotations
- **Mappers**: JPA entity <-> domain entity conversion
- **Clients**: External API integrations with resilience (retries, circuit breaker)

### Web/Transport Layer (`web/`)
- **Controllers**: Thin — validate input, delegate to use case, return response
- **Exception handlers**: Map domain/application errors to HTTP responses
- **Validation**: Use `@Valid` + Jakarta Bean Validation

```kotlin
@RestController
@RequestMapping("/api/v1/orders")
class OrderController(private val createOrder: CreateOrderUseCase) {

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    fun create(@Valid @RequestBody request: CreateOrderRequest): OrderResponse =
        createOrder.execute(request)
}
```

## Key Patterns

### Error Handling
- Use sealed classes for domain errors
- Map to RFC 7807 Problem Details in exception handler
- Never expose stack traces

```kotlin
sealed class OrderError : RuntimeException() {
    data class NotFound(val orderId: OrderId) : OrderError()
    data class InvalidState(val message: String) : OrderError()
}
```

### Testing
- **Unit tests**: Domain logic, use cases (mock repositories)
- **Integration tests**: `@SpringBootTest` + Testcontainers for DB tests
- **Slice tests**: `@WebMvcTest` for controllers, `@DataJpaTest` for repositories
- Use `AssertJ` for assertions, `MockK` for mocking

```kotlin
@Test
fun `should reject cancellation of shipped order`() {
    val order = OrderFixture.shipped()
    assertThatThrownBy { order.cancel() }
        .isInstanceOf(IllegalStateException::class.java)
}
```

### Persistence
- JPA entities are separate from domain entities
- Use `@Embeddable` for value objects
- Flyway for migrations — never use `ddl-auto` in production
- Always use parameterized queries

### Validation
- Jakarta Bean Validation on request DTOs
- Custom validators for domain-specific rules
- Validation at API boundary, domain invariants in entities

## Rules
- Constructor injection only (no `@Autowired` on fields)
- No `lateinit` for injected dependencies
- Kotlin idioms: data classes, sealed classes, extension functions, `let`/`also`/`apply`
- All dates in UTC using `java.time`
- No business logic in controllers
- No JPA annotations in domain layer
- Tests must be deterministic and parallelizable
