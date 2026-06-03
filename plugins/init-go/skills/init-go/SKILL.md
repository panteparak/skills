---
name: init-go
description: Scaffold a new Go service with clean architecture, DDD, and TDD. Use when creating a new Go backend service or microservice.
argument-hint: "[module-path] [service-name]"
disable-model-invocation: true
---

# Initialize Go Service

Scaffold a production-grade Go service for: **$ARGUMENTS**

## Step 1: Project Generation

Use official Go tooling:

```bash
mkdir $1 && cd $1
go mod init $0
```

If user provides only one argument, use it as both module path and directory name.

## Step 2: Domain-Driven Design Structure

Create the standard Go project layout with DDD:

```
$1/
├── cmd/
│   └── server/
│       └── main.go              # Entry point, wire dependencies
├── internal/                    # Private application code
│   ├── domain/                  # Core business logic (no external deps)
│   │   ├── <entity>/
│   │   │   ├── entity.go        # Domain entity, value objects
│   │   │   ├── repository.go    # Repository interface (port)
│   │   │   ├── service.go       # Domain service
│   │   │   └── errors.go        # Domain-specific errors
│   │   └── event/
│   │       └── event.go         # Domain events
│   ├── application/             # Use cases, orchestration
│   │   └── <feature>/
│   │       ├── handler.go       # Use case handlers
│   │       ├── dto.go           # Input/Output DTOs
│   │       └── handler_test.go
│   ├── infrastructure/          # External system adapters
│   │   ├── postgres/
│   │   │   ├── repository.go    # PostgreSQL repository impl
│   │   │   ├── migrations/      # SQL migrations
│   │   │   └── repository_test.go
│   │   ├── http/
│   │   │   ├── client.go        # External HTTP clients
│   │   │   └── client_test.go
│   │   └── messaging/
│   │       └── publisher.go
│   └── transport/               # Delivery layer
│       ├── http/
│       │   ├── router.go        # HTTP router setup
│       │   ├── handler.go       # HTTP handlers
│       │   ├── middleware.go    # Auth, logging, correlation ID
│       │   ├── request.go       # Request validation structs
│       │   ├── response.go      # Response helpers
│       │   └── handler_test.go
│       └── grpc/                # gRPC handlers (if needed)
├── pkg/                         # Public shared libraries
│   ├── logger/
│   │   └── logger.go            # Structured logging (slog)
│   ├── errors/
│   │   └── errors.go            # Error types and helpers
│   └── health/
│       └── health.go            # Health check
├── api/
│   └── openapi.yaml             # OpenAPI spec
├── deployments/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── k8s/                     # Kubernetes manifests
├── scripts/
│   └── migrate.sh
├── Makefile
├── .golangci.yml                # Linter config
├── go.mod
└── go.sum
```

## Step 3: Essential Dependencies

```bash
go get github.com/go-chi/chi/v5        # HTTP router (or gin, echo)
go get github.com/jackc/pgx/v5         # PostgreSQL driver
go get github.com/pressly/goose/v3     # DB migrations
go get go.uber.org/zap                  # Structured logging (or use slog)
go get github.com/go-playground/validator/v10  # Struct validation
```

For testing:
```bash
go get github.com/stretchr/testify
go get github.com/testcontainers/testcontainers-go
```

## Step 4: Base Implementation

Create:
- `main.go` with graceful shutdown, signal handling
- Structured logger setup (prefer `log/slog` for Go 1.21+)
- Config loading from env vars (use `github.com/caarlos0/env`)
- Health check endpoint (`/health`, `/ready`)
- Middleware: request ID, logging, recovery, CORS
- Error response helpers with consistent JSON structure

## Step 5: Test Infrastructure

Set up:
- `testcontainers` helper for PostgreSQL in integration tests
- Table-driven test examples
- Test helpers for HTTP handler testing
- `Makefile` targets: `test`, `test-integration`, `test-coverage`, `lint`

## Step 6: TDD Starter

Create a sample domain (e.g., `health` or `ping`) with full TDD cycle.

## Step 7: Documentation & Tooling

- `README.md` with setup, architecture, run, test instructions
- `.golangci.yml` with curated linter set
- `Makefile` with: build, run, test, lint, migrate, docker-build
- `Dockerfile` with multi-stage build
- `docs/adr/` directory

## Rules
- Accept interfaces, return structs
- Keep `internal/domain/` free of external dependencies
- Use table-driven tests
- Errors are values — wrap with context using `fmt.Errorf("...: %w", err)`
- No `init()` functions — explicit dependency injection in `main.go`
- Use `context.Context` for cancellation and request-scoped values
- Prefer `log/slog` (stdlib) for structured logging in Go 1.21+
