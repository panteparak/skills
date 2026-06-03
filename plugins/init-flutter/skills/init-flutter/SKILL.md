---
name: init-flutter
description: Scaffold a new Flutter mobile/web app with clean architecture and testing. Use when creating a new Flutter application.
argument-hint: "[project-name] [org-domain]"
disable-model-invocation: true
---

# Initialize Flutter Project

Scaffold a production-grade Flutter application for: **$ARGUMENTS**

## Step 1: Project Generation

Use official Flutter CLI:

```bash
flutter create --org $1 --project-name $0 --platforms ios,android,web $0
cd $0
```

Default org domain: `com.example` if not provided.

## Step 2: Essential Dependencies

```bash
flutter pub add flutter_riverpod riverpod_annotation go_router freezed_annotation \
  json_annotation dio shared_preferences flutter_secure_storage intl
flutter pub add -d riverpod_generator build_runner freezed json_serializable \
  flutter_lints mocktail bloc_test
```

## Step 3: Clean Architecture Structure

```
lib/
├── main.dart                      # App entry point
├── app.dart                       # MaterialApp with router + providers
├── core/
│   ├── constants/                 # App-wide constants
│   ├── errors/                    # Failure classes, exceptions
│   │   ├── failures.dart
│   │   └── exceptions.dart
│   ├── network/                   # Dio client, interceptors
│   │   ├── api_client.dart
│   │   └── interceptors.dart
│   ├── router/                    # GoRouter config
│   │   └── app_router.dart
│   ├── theme/                     # ThemeData, colors, typography
│   │   ├── app_theme.dart
│   │   └── app_colors.dart
│   └── utils/                     # Extensions, helpers
│       └── extensions.dart
├── features/
│   └── <feature>/
│       ├── domain/
│       │   ├── entities/          # Pure Dart domain objects
│       │   ├── repositories/     # Repository interfaces (abstract)
│       │   └── usecases/         # Use case classes
│       ├── data/
│       │   ├── models/           # Freezed data models (JSON)
│       │   ├── datasources/     # Remote + local data sources
│       │   └── repositories/    # Repository implementations
│       ├── presentation/
│       │   ├── providers/       # Riverpod providers
│       │   ├── screens/         # Full-page widgets
│       │   ├── widgets/         # Feature-specific widgets
│       │   └── state/           # State classes (if complex)
│       └── tests/               # Colocated tests
├── shared/
│   └── widgets/                 # Shared UI components
test/
├── core/
├── features/
│   └── <feature>/
│       ├── domain/
│       ├── data/
│       └── presentation/
├── helpers/                     # Test helpers, mocks
│   ├── pump_app.dart           # Widget test helper
│   └── mocks.dart
└── fixtures/                   # JSON fixtures for tests
```

## Step 4: Base Implementation

Create:
- `AppRouter` with `GoRouter` and route guards
- `ApiClient` with Dio, interceptors (auth, logging, error)
- `Failure` sealed class for typed error handling
- `AppTheme` with Material 3 theming
- Base Riverpod providers (auth state, connectivity)

## Step 5: Test Infrastructure

- Widget test helper (`pumpApp`) that wraps with `ProviderScope` + `MaterialApp`
- Mock generation setup with `mocktail`
- Example unit test (use case), widget test (screen), integration test
- `test/fixtures/` for JSON response fixtures

## Step 6: Code Generation

Set up `build_runner` for:
- Freezed models (immutable data classes)
- JSON serialization
- Riverpod code generation

Add to `Makefile`:
```makefile
generate:
	dart run build_runner build --delete-conflicting-outputs
watch:
	dart run build_runner watch --delete-conflicting-outputs
```

## Step 7: Documentation

- `README.md` with setup, run, test, build, architecture
- Flavor/environment setup documentation (dev, staging, prod)

## Rules
- Use Riverpod for state management (not setState or BLoC for new projects)
- Use Freezed for all data models
- Use GoRouter for navigation
- Business logic in use cases, never in widgets
- Repository pattern for all data access
- Fail with typed Failures, never raw exceptions in domain layer
