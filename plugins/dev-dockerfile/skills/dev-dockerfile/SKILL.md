---
name: dev-dockerfile
description: Create production-grade Dockerfiles with multi-stage builds, security hardening, and optimal layer caching. Use when writing or improving Dockerfiles.
argument-hint: "[language-or-framework]"
---

# Production Dockerfile

Create a production-grade Dockerfile for: **$ARGUMENTS**

## Process

1. **Identify the stack** — language, framework, runtime requirements
2. **Choose base image** — minimal, official, specific version tag
3. **Design stages** — builder (compile/install) → production (runtime only)
4. **Optimize layers** — cache dependencies before copying source
5. **Harden security** — non-root user, no secrets in image, minimal attack surface

## Multi-Stage Build Pattern

### Python (Django / FastAPI with uv)
```dockerfile
# ---- Builder ----
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

# Install dependencies first (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

# Copy source and collect static
COPY . .
RUN uv run manage.py collectstatic --noinput

# ---- Production ----
FROM python:3.12-slim
RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app
WORKDIR /app

COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH"

USER app
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application"]
```

### Go
```dockerfile
# ---- Builder ----
FROM golang:1.23-alpine AS builder
RUN apk add --no-cache git ca-certificates
WORKDIR /app

# Cache module downloads
COPY go.mod go.sum ./
RUN go mod download

# Build static binary
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /server ./cmd/server

# ---- Production ----
FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /server /server

USER 65534:65534
EXPOSE 8080
ENTRYPOINT ["/server"]
```

### Kotlin / Spring Boot
```dockerfile
# ---- Builder ----
FROM gradle:8-jdk21-alpine AS builder
WORKDIR /app

# Cache Gradle dependencies
COPY build.gradle.kts settings.gradle.kts gradle.properties ./
COPY gradle ./gradle
RUN gradle dependencies --no-daemon

# Build application
COPY . .
RUN gradle bootJar --no-daemon -x test

# ---- Production ----
FROM eclipse-temurin:21-jre-alpine
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app

COPY --from=builder --chown=app:app /app/build/libs/*.jar app.jar

USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q --spider http://localhost:8080/actuator/health || exit 1
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Node.js / Next.js
```dockerfile
# ---- Dependencies ----
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# ---- Builder ----
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- Production ----
FROM node:20-alpine
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app

COPY --from=deps --chown=app:app /app/node_modules ./node_modules
COPY --from=builder --chown=app:app /app/.next ./.next
COPY --from=builder --chown=app:app /app/public ./public
COPY --from=builder --chown=app:app /app/package.json ./

USER app
EXPOSE 3000
CMD ["npm", "start"]
```

## Layer Caching Strategy

```
# GOOD — Dependencies cached independently from source code
COPY package.json package-lock.json ./   # Changes rarely
RUN npm ci                                # Cached unless lock file changes
COPY . .                                  # Changes often — only this layer rebuilds

# BAD — Everything rebuilds every time
COPY . .
RUN npm ci
```

**Rule**: Copy dependency manifests → install → then copy source.

## Security Hardening Checklist

- [ ] **Non-root user**: Create `app` user, `USER app` before CMD
- [ ] **Minimal base image**: Use `-slim` or `-alpine` variants, or `scratch` for Go
- [ ] **Pinned versions**: `python:3.12.8-slim`, not `python:latest`
- [ ] **No secrets in image**: Use build args or runtime env vars, never `COPY .env`
- [ ] **No dev dependencies**: `--no-dev`, `--only=production`, `-x test`
- [ ] **Read-only filesystem**: Pair with `--read-only` in docker-compose/K8s
- [ ] **HEALTHCHECK**: Add Docker-native health check instruction
- [ ] **`.dockerignore`**: Exclude `.git`, `node_modules`, `.env`, `__pycache__`, `*.pyc`

## .dockerignore Template

```
.git
.github
.vscode
.idea
*.md
docker-compose*.yml
.env*
__pycache__
*.pyc
node_modules
.next
build
dist
coverage
.pytest_cache
.mypy_cache
.ruff_cache
```

## docker-compose.yml Pattern

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production        # Use specific stage
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    read_only: true             # Security: read-only filesystem
    tmpfs:
      - /tmp                    # Writable tmp dir

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
```

## Rules
- Always use multi-stage builds — separate build deps from runtime
- Pin exact image versions (digest or tag), never use `latest`
- Non-root user is mandatory
- `.dockerignore` is mandatory
- HEALTHCHECK for every service
- No secrets baked into images
- Optimize for layer cache hit rate
- Final image should be as small as possible
