---
name: dev-flutter
description: Develop features in Flutter apps using Riverpod, clean architecture, and TDD. Use when writing Flutter/Dart code.
argument-hint: "[feature-description]"
---

# Flutter Development

Implement the following feature: **$ARGUMENTS**

## Development Workflow

1. **Write failing test** — unit test for use case or widget test
2. **Implement domain layer** — entities, repository interface, use case
3. **Implement data layer** — models (Freezed), repository impl, data source
4. **Implement presentation** — providers, widgets, screens
5. **Run code generation** — `dart run build_runner build`

## Architecture Layers

### Domain (Pure Dart — no Flutter)
```dart
// features/orders/domain/entities/order.dart
class Order {
  final String id;
  final List<OrderItem> items;
  final OrderStatus status;
  final DateTime createdAt;

  Order({required this.id, required this.items, required this.status, required this.createdAt});

  double get totalAmount => items.fold(0, (sum, item) => sum + item.subtotal);
  bool get canBeCancelled => status == OrderStatus.pending || status == OrderStatus.confirmed;
}

// features/orders/domain/repositories/order_repository.dart
abstract class OrderRepository {
  Future<List<Order>> getOrders();
  Future<Order> getOrderById(String id);
  Future<Order> createOrder(CreateOrderParams params);
  Future<void> cancelOrder(String id);
}

// features/orders/domain/usecases/create_order.dart
class CreateOrderUseCase {
  final OrderRepository _repository;
  CreateOrderUseCase(this._repository);

  Future<Either<Failure, Order>> call(CreateOrderParams params) async {
    try {
      final order = await _repository.createOrder(params);
      return Right(order);
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    }
  }
}
```

### Data (Freezed models + API)
```dart
// features/orders/data/models/order_model.dart
@freezed
class OrderModel with _$OrderModel {
  const factory OrderModel({
    required String id,
    required List<OrderItemModel> items,
    required String status,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _OrderModel;

  factory OrderModel.fromJson(Map<String, dynamic> json) => _$OrderModelFromJson(json);
}

extension OrderModelX on OrderModel {
  Order toDomain() => Order(
    id: id,
    items: items.map((i) => i.toDomain()).toList(),
    status: OrderStatus.values.byName(status),
    createdAt: createdAt,
  );
}
```

### Presentation (Riverpod + Widgets)
```dart
// features/orders/presentation/providers/order_providers.dart
@riverpod
Future<List<Order>> orders(Ref ref) async {
  final repository = ref.watch(orderRepositoryProvider);
  return repository.getOrders();
}

@riverpod
class OrderNotifier extends _$OrderNotifier {
  @override
  FutureOr<Order?> build() => null;

  Future<void> createOrder(CreateOrderParams params) async {
    state = const AsyncLoading();
    final useCase = ref.read(createOrderUseCaseProvider);
    final result = await useCase(params);
    state = result.fold(
      (failure) => AsyncError(failure, StackTrace.current),
      (order) => AsyncData(order),
    );
  }
}

// features/orders/presentation/screens/order_list_screen.dart
class OrderListScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ordersAsync = ref.watch(ordersProvider);
    return ordersAsync.when(
      data: (orders) => ListView.builder(
        itemCount: orders.length,
        itemBuilder: (_, i) => OrderCard(order: orders[i]),
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => ErrorDisplay(message: e.toString()),
    );
  }
}
```

## Testing

```dart
// Unit test for use case
void main() {
  late CreateOrderUseCase useCase;
  late MockOrderRepository mockRepo;

  setUp(() {
    mockRepo = MockOrderRepository();
    useCase = CreateOrderUseCase(mockRepo);
  });

  test('should return Order on success', () async {
    when(() => mockRepo.createOrder(any())).thenAnswer((_) async => tOrder);
    final result = await useCase(tParams);
    expect(result, Right(tOrder));
    verify(() => mockRepo.createOrder(tParams)).called(1);
  });
}

// Widget test
void main() {
  testWidgets('OrderListScreen shows orders', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [ordersProvider.overrideWith((_) => [testOrder])],
        child: const MaterialApp(home: OrderListScreen()),
      ),
    );
    expect(find.byType(OrderCard), findsOneWidget);
  });
}
```

## Rules
- Riverpod for state management (not setState for anything beyond trivial)
- Freezed for all data models
- Business logic in use cases, never in widgets
- Repository pattern for all data access
- `Either<Failure, T>` for error handling in domain layer
- Run `build_runner` after changing Freezed/Riverpod annotated code
- Widget tests for all screens, unit tests for all use cases
- Use `mocktail` for mocking (not mockito)
