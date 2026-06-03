---
name: init-springboot
description: Scaffold a new Spring Boot + Kotlin project with DDD, TDD, and clean architecture. Use when creating a new Spring Boot backend service.
argument-hint: "[project-name] [group-id]"
disable-model-invocation: true
---

# Initialize Spring Boot + Kotlin Project

Scaffold a production-grade Spring Boot + Kotlin project for: **$ARGUMENTS**

## Step 1: Project Generation

Use Spring Initializr CLI via curl to generate the project:

```bash
curl https://start.spring.io/starter.zip \
  -d type=gradle-project \
  -d language=kotlin \
  -d bootVersion=3.4.3 \
  -d baseDir=$0 \
  -d groupId=$1 \
  -d artifactId=$0 \
  -d name=$0 \
  -d packageName=$1.$0 \
  -d javaVersion=21 \
  -d dependencies=web,data-jpa,validation,actuator,testcontainers,security,flyway,postgresql \
  -o $0.zip && unzip $0.zip && rm $0.zip
```

If the user did not provide a group-id, use `com.example`.

## Step 2: Domain-Driven Design Structure

Restructure into package-by-feature with DDD layers:

```
src/main/kotlin/<package>/
├── Application.kt
├── shared/
│   ├── config/              # Spring config, beans, security
│   ├── exception/           # Global exception handler, error models
│   ├── web/                 # CORS, filters, interceptors
│   └── persistence/         # Base entity, auditing config
├── <feature>/               # One package per bounded context
│   ├── domain/
│   │   ├── model/           # Entities, value objects, aggregates
│   │   ├── port/            # Repository interfaces, service ports
│   │   └── event/           # Domain events
│   ├── application/
│   │   ├── service/         # Use cases, application services
│   │   ├── dto/             # Request/Response DTOs
│   │   └── mapper/          # Domain <-> DTO mappers
│   ├── infrastructure/
│   │   ├── persistence/     # JPA repositories, entities, mappers
│   │   ├── client/          # External API clients
│   │   └── messaging/       # Event publishers, consumers
│   └── web/
│       ├── controller/      # REST controllers
│       └── validation/      # Custom validators
```

## Step 3: Base Configuration Files

Create these essential files:
- `application.yml` with profiles (dev, test, prod)
- `application-test.yml` with Testcontainers config
- `docker-compose.yml` with PostgreSQL, Redis (if needed)
- `.editorconfig` with Kotlin conventions
- `Makefile` with common commands (build, test, run, lint)
- `detekt.yml` for Kotlin static analysis
- Flyway migration directory: `src/main/resources/db/migration/`
- Initial migration: `V1__init.sql`

## Step 4: Base Classes

Create:
- Global exception handler with RFC 7807 Problem Details
- Base audit entity with `createdAt`, `updatedAt`
- Structured logging config with correlation IDs
- Health check and readiness endpoints (via Actuator)
- Security config skeleton (permit-all initially, document hardening steps)

## Step 5: Test Infrastructure

Set up:
- `AbstractIntegrationTest` base class using `@Testcontainers` + PostgreSQL
- `TestFixtures` factory for creating test data
- Example unit test and integration test for a sample feature
- `src/test/resources/application-test.yml`

## Step 6: TDD Starter

Create a minimal sample feature (e.g., `healthcheck` or `ping`) following full TDD:
1. Write failing test first
2. Implement minimal production code
3. Refactor

## Step 7: Documentation

- `README.md` with: project purpose, prerequisites, setup, run, test, architecture overview
- `docs/adr/` directory with ADR template (`0001-record-architecture-decisions.md`)
- `.github/pull_request_template.md`

## Rules
- Always use Kotlin idioms (data classes, sealed classes, extension functions)
- Prefer immutable data structures
- Use constructor injection exclusively
- Never use `lateinit` for dependencies
- All dates in UTC, use `java.time` API
