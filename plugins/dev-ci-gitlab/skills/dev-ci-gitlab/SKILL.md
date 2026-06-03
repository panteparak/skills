---
name: dev-ci-gitlab
description: Create GitLab CI/CD pipelines for testing, linting, building, and deploying applications. Use when setting up or improving GitLab CI pipelines.
argument-hint: "[language-or-workflow-type]"
---

# GitLab CI/CD

Create CI/CD pipelines for: **$ARGUMENTS**

## Process

1. **Identify the stack** — language, test framework, deployment target
2. **Design pipeline stages** — lint → test → build → deploy
3. **Optimize for speed** — caching, parallel jobs, rules-based execution
4. **Add quality gates** — block merge on failures

## Pipeline Templates

### Python (Django / FastAPI)

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - build
  - deploy

variables:
  POSTGRES_DB: test
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
  DATABASE_URL: "postgres://postgres:postgres@postgres:5432/test"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  UV_CACHE_DIR: "$CI_PROJECT_DIR/.cache/uv"

# ------------------------------------------------------------------------------
# Templates (reusable)
# ------------------------------------------------------------------------------
.python-setup: &python-setup
  image: python:3.12-slim
  before_script:
    - pip install uv
    - uv sync --frozen
  cache:
    key:
      files:
        - uv.lock
    paths:
      - .cache/uv
      - .venv

# ------------------------------------------------------------------------------
# Lint
# ------------------------------------------------------------------------------
ruff:
  <<: *python-setup
  stage: lint
  script:
    - uv run ruff check .
    - uv run ruff format --check .

mypy:
  <<: *python-setup
  stage: lint
  script:
    - uv run mypy .

# ------------------------------------------------------------------------------
# Test
# ------------------------------------------------------------------------------
test:
  <<: *python-setup
  stage: test
  services:
    - name: postgres:16-alpine
      alias: postgres
  variables:
    DJANGO_SETTINGS_MODULE: config.settings.test
  script:
    - uv run pytest --cov --cov-report=xml --cov-report=term --junitxml=report.xml
  artifacts:
    when: always
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  coverage: '/(?i)total.*? (100(?:\.0+)?\%|[1-9]?\d(?:\.\d+)?\%)$/'

# ------------------------------------------------------------------------------
# Build
# ------------------------------------------------------------------------------
build-image:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build
        --cache-from $CI_REGISTRY_IMAGE:latest
        --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
        --tag $CI_REGISTRY_IMAGE:latest
        .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Go

```yaml
stages:
  - lint
  - test
  - build

variables:
  POSTGRES_DB: test
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
  GOPATH: "$CI_PROJECT_DIR/.go"

.go-setup: &go-setup
  image: golang:1.23-alpine
  before_script:
    - apk add --no-cache git gcc musl-dev
  cache:
    key:
      files:
        - go.sum
    paths:
      - .go/pkg/mod

lint:
  <<: *go-setup
  stage: lint
  image: golangci/golangci-lint:latest
  script:
    - golangci-lint run --timeout 5m

test-unit:
  <<: *go-setup
  stage: test
  script:
    - go test -v -short -race -coverprofile=coverage.out ./...
    - go tool cover -func=coverage.out
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  coverage: '/total:\s+\(statements\)\s+(\d+\.\d+)%/'

test-integration:
  <<: *go-setup
  stage: test
  services:
    - name: postgres:16-alpine
      alias: postgres
  variables:
    DATABASE_URL: "postgres://postgres:postgres@postgres:5432/test?sslmode=disable"
  script:
    - go test -v -race ./...

build:
  <<: *go-setup
  stage: build
  script:
    - CGO_ENABLED=0 go build -ldflags="-s -w" -o bin/server ./cmd/server
  artifacts:
    paths:
      - bin/server
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

build-image:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  needs: [test-unit, test-integration]
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Kotlin / Spring Boot

```yaml
stages:
  - test
  - build

variables:
  POSTGRES_DB: test
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
  GRADLE_USER_HOME: "$CI_PROJECT_DIR/.gradle"

.gradle-setup: &gradle-setup
  image: gradle:8-jdk21-alpine
  cache:
    key:
      files:
        - gradle/wrapper/gradle-wrapper.properties
        - build.gradle.kts
    paths:
      - .gradle/caches
      - .gradle/wrapper

test:
  <<: *gradle-setup
  stage: test
  services:
    - name: postgres:16-alpine
      alias: postgres
  variables:
    SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/test
    SPRING_DATASOURCE_USERNAME: postgres
    SPRING_DATASOURCE_PASSWORD: postgres
  script:
    - gradle check test --no-daemon
  artifacts:
    when: always
    reports:
      junit: build/test-results/test/*.xml

build:
  <<: *gradle-setup
  stage: build
  script:
    - gradle bootJar --no-daemon -x test
  artifacts:
    paths:
      - build/libs/*.jar
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

build-image:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  needs: [test]
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Next.js / Node.js

```yaml
stages:
  - lint
  - test
  - build

variables:
  NPM_CONFIG_CACHE: "$CI_PROJECT_DIR/.cache/npm"

.node-setup: &node-setup
  image: node:20-alpine
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - .cache/npm
      - node_modules

lint:
  <<: *node-setup
  stage: lint
  script:
    - npm ci
    - npm run lint
    - npm run type-check

test:
  <<: *node-setup
  stage: test
  script:
    - npm ci
    - npm test -- --coverage
  artifacts:
    when: always
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'

e2e:
  stage: test
  image: mcr.microsoft.com/playwright:v1.49.0-noble
  needs: [lint]
  script:
    - npm ci
    - npm run build
    - npx playwright test
  artifacts:
    when: failure
    paths:
      - playwright-report/
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

build:
  <<: *node-setup
  stage: build
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - .next/
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## GitLab CI Optimization Patterns

### Caching (Key Differences from GitHub Actions)

GitLab caching is file-based and shared across pipelines on the same runner:

```yaml
# Cache by lock file hash — rebuild only when deps change
cache:
  key:
    files:
      - uv.lock            # Python
      - go.sum              # Go
      - package-lock.json   # Node
      - gradle.lockfile     # Gradle
  paths:
    - .venv                 # Python virtualenv
    - .go/pkg/mod           # Go modules
    - node_modules          # Node packages
    - .gradle/caches        # Gradle

# Per-branch caching with fallback
cache:
  key: "$CI_COMMIT_REF_SLUG"
  paths:
    - node_modules
  policy: pull-push         # Default: download + upload
```

### DAG (Directed Acyclic Graph) — Parallel Execution

```yaml
# Use `needs` to run jobs as soon as dependencies finish
# (instead of waiting for entire stage to complete)
test-unit:
  stage: test
  needs: [lint]             # Starts as soon as lint finishes

test-integration:
  stage: test
  needs: [lint]             # Runs in parallel with test-unit

build:
  stage: build
  needs: [test-unit, test-integration]  # Waits for both tests
```

### Rules (Replaces `only`/`except`)

```yaml
# Run on MR and default branch only
rules:
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# Run only when specific files change
rules:
  - changes:
      - src/**/*
      - tests/**/*
      - pyproject.toml

# Skip for draft MRs
rules:
  - if: $CI_MERGE_REQUEST_TITLE =~ /^Draft:/
    when: never
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"

# Manual deploy to production
deploy-prod:
  stage: deploy
  script: ./deploy.sh production
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
  environment:
    name: production
    url: https://app.example.com
```

### Interruptible Pipelines

```yaml
# Cancel running pipeline when a new commit is pushed
workflow:
  auto_cancel:
    on_new_commit: interruptible

# Mark jobs as interruptible (safe to cancel)
lint:
  interruptible: true
  # ...

# Non-interruptible (e.g., deploy — never cancel mid-deploy)
deploy:
  interruptible: false
```

### Docker-in-Docker (DinD) for Builds

```yaml
build-image:
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
    # Use BuildKit for faster builds
    DOCKER_BUILDKIT: 1
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build
        --cache-from $CI_REGISTRY_IMAGE:latest
        --build-arg BUILDKIT_INLINE_CACHE=1
        -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
        -t $CI_REGISTRY_IMAGE:latest
        .
    - docker push $CI_REGISTRY_IMAGE --all-tags
```

### Includes & Templates (DRY)

```yaml
# .gitlab-ci.yml — compose from templates
include:
  - local: .gitlab/ci/lint.yml
  - local: .gitlab/ci/test.yml
  - local: .gitlab/ci/build.yml
  - local: .gitlab/ci/deploy.yml

# Or use GitLab's built-in templates
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
```

### Environments & Deploy

```yaml
deploy-staging:
  stage: deploy
  script:
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  environment:
    name: staging
    url: https://staging.example.com
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

deploy-production:
  stage: deploy
  script:
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  environment:
    name: production
    url: https://app.example.com
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
  needs: [deploy-staging]
```

## Merge Request Settings

Configure in GitLab project settings (Settings → Merge requests):
- Pipelines must succeed
- All discussions must be resolved
- Require approval from code owners
- Enable merge trains (optional — serializes merges)

## GitLab vs GitHub CI Key Differences

| Concept | GitHub Actions | GitLab CI |
|---------|---------------|-----------|
| Config file | `.github/workflows/*.yml` | `.gitlab-ci.yml` |
| Parallel jobs | Jobs in same step | `needs:` DAG keyword |
| Cancel stale | `concurrency: cancel-in-progress` | `interruptible: true` + workflow auto_cancel |
| Conditional | `if:` on jobs | `rules:` with `if:` / `changes:` |
| Services | `services:` on jobs | `services:` on jobs (similar) |
| Registry | `ghcr.io` | `$CI_REGISTRY` (built-in) |
| Auth | `${{ secrets.GITHUB_TOKEN }}` | `$CI_REGISTRY_USER` / `$CI_REGISTRY_PASSWORD` |
| Artifacts | `upload-artifact` action | `artifacts:` keyword (native) |
| Caching | Action-based (`actions/cache`) | `cache:` keyword (native, file-key) |
| Reuse | Composite actions, reusable workflows | `include:`, YAML anchors, `extends:` |
| Environments | `environment:` on jobs | `environment:` with built-in review apps |
| Security scan | Third-party actions | Built-in SAST/DAST templates |

## Rules
- Use `rules:` instead of deprecated `only:`/`except:`
- Use `needs:` DAG for parallel execution — don't wait for entire stages
- Cache by lock file hash — `key: { files: [lockfile] }`
- Use `interruptible: true` on lint/test jobs to cancel stale pipelines
- Built-in container registry — `$CI_REGISTRY_IMAGE` is free
- Use `include:` to split large pipelines into files
- Artifacts with `reports:` for test results visible in MR UI
- Use `when: manual` for production deploys — require human approval
- Never store secrets in `.gitlab-ci.yml` — use CI/CD Variables (masked + protected)
- Enable built-in SAST/dependency scanning templates for free security checks
