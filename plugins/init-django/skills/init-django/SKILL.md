---
name: init-django
description: Scaffold a new Django + DRF project with DDD structure, sub-apps, TDD, and production-ready config using uv. Use when creating a new Django/Python backend service.
argument-hint: "[project-name]"
disable-model-invocation: true
---

# Initialize Django + Django REST Framework Project

Scaffold a production-grade Django + DRF project for: **$ARGUMENTS**

## Step 1: Project Generation with uv

Use `uv` (fast Python package manager) instead of pip/venv:

```bash
uv init $0 && cd $0
```

### Add core dependencies:

```bash
# Framework
uv add django djangorestframework drf-spectacular

# Database
uv add psycopg2-binary

# API & Middleware
uv add django-filter django-cors-headers django-environ

# Production server
uv add gunicorn

# Async tasks
uv add "celery[redis]"

# Observability
uv add django-structlog structlog django-health-check whitenoise "sentry-sdk[django]"

# Storage
uv add "django-storages[s3]"
```

### Add dev dependencies:

```bash
uv add --group dev django-extensions ipython

uv add --group test pytest pytest-django pytest-cov factory-boy faker
```

### Generate Django project:

```bash
uv run django-admin startproject config .
```

> **Note**: All Django commands use `uv run` prefix:
> `uv run manage.py runserver`, `uv run manage.py migrate`, etc.

## Step 2: Domain-Driven Sub-App Architecture

Each bounded context becomes a **top-level Django app**. Each app is further broken into **sub-apps** for separation of concerns. Use `uv run manage.py startapp` for every sub-app:

```bash
# Example: "users" bounded context with sub-apps
mkdir -p apps/users
uv run manage.py startapp accounts apps/users/accounts
uv run manage.py startapp profiles apps/users/profiles
uv run manage.py startapp notifications apps/users/notifications

# Example: "products" bounded context with sub-apps
mkdir -p apps/products
uv run manage.py startapp catalog apps/products/catalog
uv run manage.py startapp inventory apps/products/inventory
uv run manage.py startapp pricing apps/products/pricing

# Shared/core app
uv run manage.py startapp core apps/core
```

### Full Project Structure

```
$0/
├── config/                          # Django project config
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                  # Shared settings (DRF, middleware, etc.)
│   │   ├── development.py           # DEBUG=True, CORS permissive
│   │   ├── test.py                  # In-memory DB, fast password hasher
│   │   └── production.py            # Security, HTTPS, strict CORS
│   ├── urls.py                      # Root URL conf — mounts bounded contexts
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── core/                        # Shared cross-cutting concerns
│   │   ├── models.py                # TimeStampedModel, SoftDeleteModel
│   │   ├── exceptions.py            # Custom DRF exception handler
│   │   ├── pagination.py            # Standard pagination classes
│   │   ├── permissions.py           # Shared permission classes
│   │   ├── renderers.py             # Consistent response envelope
│   │   ├── throttling.py            # Rate limiting classes
│   │   ├── middleware/
│   │   │   ├── correlation_id.py    # Request correlation ID
│   │   │   └── request_logging.py   # Structured request logging
│   │   └── utils/
│   │       ├── validators.py        # Shared validators
│   │       └── helpers.py
│   │
│   ├── users/                       # Bounded context: Users
│   │   ├── __init__.py
│   │   ├── urls.py                  # Mounts sub-app URLs
│   │   │
│   │   ├── accounts/               # Sub-app: Authentication & accounts
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py           # CustomUser (AbstractUser)
│   │   │   ├── managers.py         # CustomUserManager
│   │   │   ├── admin.py
│   │   │   ├── services.py         # Registration, password reset logic
│   │   │   ├── selectors.py        # User queries (get_user_by_email, etc.)
│   │   │   ├── api/
│   │   │   │   ├── serializers.py   # DRF serializers
│   │   │   │   ├── views.py         # DRF ViewSets / APIViews
│   │   │   │   ├── urls.py          # Sub-app URL patterns
│   │   │   │   └── filters.py       # django-filter filtersets
│   │   │   ├── tests/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_models.py
│   │   │   │   ├── test_services.py
│   │   │   │   ├── test_selectors.py
│   │   │   │   ├── test_api.py
│   │   │   │   └── factories.py     # factory_boy factories
│   │   │   └── migrations/
│   │   │
│   │   ├── profiles/               # Sub-app: User profiles
│   │   │   ├── models.py           # Profile, Address, Preferences
│   │   │   ├── services.py
│   │   │   ├── selectors.py
│   │   │   ├── api/
│   │   │   │   ├── serializers.py
│   │   │   │   ├── views.py
│   │   │   │   └── urls.py
│   │   │   ├── tests/
│   │   │   │   ├── test_models.py
│   │   │   │   ├── test_api.py
│   │   │   │   └── factories.py
│   │   │   └── migrations/
│   │   │
│   │   └── notifications/          # Sub-app: User notifications
│   │       ├── models.py           # Notification, NotificationPreference
│   │       ├── services.py         # Send, mark read, batch notify
│   │       ├── tasks.py            # Celery async tasks
│   │       ├── api/
│   │       │   ├── serializers.py
│   │       │   ├── views.py
│   │       │   └── urls.py
│   │       ├── tests/
│   │       └── migrations/
│   │
│   └── <other_context>/            # Repeat pattern per bounded context
│       ├── __init__.py
│       ├── urls.py
│       ├── <sub_app_a>/
│       ├── <sub_app_b>/
│       └── <sub_app_c>/
│
├── tests/                           # Project-level integration tests
│   ├── conftest.py                  # Shared fixtures, api client
│   └── test_health.py
│
├── gunicorn.conf.py                 # Gunicorn production config
├── docker-compose.yml               # PostgreSQL, Redis, Mailhog
├── Dockerfile
├── Makefile
├── pyproject.toml                   # Project metadata + dependency groups + tool config
├── uv.lock                          # Locked dependency versions (commit this)
├── manage.py
└── .env.example
```

## Step 3: Settings Configuration

### settings/base.py — Shared settings

```python
import environ

env = environ.Env()

# ==============================================================================
# INSTALLED APPS
# ==============================================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",         # Before staticfiles
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.migrations",
    "django_structlog",
    "storages",
    # Local apps
    "apps.core",
    # ... bounded context sub-apps
]

# ==============================================================================
# MIDDLEWARE — ORDER MATTERS
# ==============================================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",          # FIRST — before all others
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",      # After SecurityMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_structlog.middlewares.RequestMiddleware",  # Structured logging
]

# ==============================================================================
# DJANGO REST FRAMEWORK
# ==============================================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "$0 API",
    "DESCRIPTION": "API documentation for $0",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ==============================================================================
# CORS — Base (overridden per environment)
# ==============================================================================

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "origin",
    "x-csrftoken",
    "x-requested-with",
    "x-correlation-id",
]
# Restrict CORS to API endpoints only
CORS_URLS_REGEX = r"^/api/.*$"

# ==============================================================================
# STATIC FILES (WhiteNoise)
# ==============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ==============================================================================
# STRUCTLOG — Structured Logging
# ==============================================================================

import structlog

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),  # Override in production
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

DJANGO_STRUCTLOG_COMMAND_LOGGING_ENABLED = True
```

### settings/development.py

```python
from .base import *

DEBUG = True

# CORS — permissive in development
CORS_ALLOW_ALL_ORIGINS = True

# Additional dev apps
INSTALLED_APPS += [
    "django_extensions",
]

# Database — local PostgreSQL
DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://postgres:postgres@localhost:5432/$0"),
}
```

### settings/production.py

```python
from .base import *

DEBUG = False

# CORS — strict in production, loaded from environment
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_ALL_ORIGINS = False

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Sentry
import sentry_sdk

sentry_sdk.init(
    dsn=env("SENTRY_DSN", default=""),
    traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1),
    profiles_sample_rate=env.float("SENTRY_PROFILES_SAMPLE_RATE", default=0.1),
    send_default_pii=False,
)

# Static files — WhiteNoise compression
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
}
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")

# Structlog — JSON output in production
import structlog
LOGGING["formatters"]["json"]["processor"] = structlog.processors.JSONRenderer()
```

### settings/test.py

```python
from .base import *

DEBUG = False

# Fast password hashing for tests
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# CORS — disabled in tests
CORS_ALLOW_ALL_ORIGINS = True

# Database — use in-memory SQLite or fast PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
```

## Step 4: Gunicorn Production Configuration

Create `gunicorn.conf.py` at project root:

```python
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 4
worker_tmp_dir = "/dev/shm"  # Faster worker heartbeat in containers

# Timeouts
timeout = 30
graceful_timeout = 30
keepalive = 5

# Requests
max_requests = 1000           # Restart worker after N requests (prevents memory leaks)
max_requests_jitter = 50      # Random jitter to avoid all workers restarting at once

# Logging
accesslog = "-"               # stdout
errorlog = "-"                # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "$0"

# Preload app for faster worker spawning (uses more memory)
preload_app = True
```

Run with: `uv run gunicorn config.wsgi:application`

## Step 5: URL Mounting Pattern

Root `config/urls.py` mounts bounded contexts:
```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/products/", include("apps.products.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(), name="swagger-ui"),
    path("health/", include("health_check.urls")),
]
```

Bounded context `apps/users/urls.py` mounts sub-apps:
```python
urlpatterns = [
    path("accounts/", include("apps.users.accounts.api.urls")),
    path("profiles/", include("apps.users.profiles.api.urls")),
    path("notifications/", include("apps.users.notifications.api.urls")),
]
```

## Step 6: Base Classes & Core App

Create in `apps/core/`:

**models.py** — Abstract base models:
- `TimeStampedModel`: `created_at`, `updated_at` (auto)
- `SoftDeleteModel`: `deleted_at`, custom manager filtering deleted

**exceptions.py** — Custom DRF exception handler:
- Wrap all errors in consistent envelope: `{"error": {"code": ..., "message": ..., "details": ...}}`
- Map Django `ValidationError` to DRF format
- Log 5xx errors with correlation ID

**pagination.py** — Standard pagination:
- `StandardPagination` with `page_size`, `max_page_size`
- Cursor pagination option for large datasets

**permissions.py** — Reusable permissions:
- `IsOwner`, `IsAdminOrReadOnly`, etc.

## Step 7: Services & Selectors Pattern

Enforce strict separation in every sub-app:

- **services.py** — Write operations (create, update, delete). Contains business logic. Takes validated data, returns domain objects. Called by views after serializer validation.
- **selectors.py** — Read operations (list, detail, filter). Query logic isolated from views. Returns QuerySets for composability.
- **views.py** — Thin. Validates input (serializer), delegates to service/selector, returns response.
- **serializers.py** — Input validation and output representation only. No business logic.

## Step 8: Test Infrastructure

Set up with pytest-django:

**conftest.py** (root):
```python
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user_factory):
    user = user_factory()
    api_client.force_authenticate(user=user)
    return api_client
```

**Factory pattern** (per sub-app `tests/factories.py`):
```python
import factory
from faker import Faker

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "accounts.CustomUser"
    email = factory.LazyAttribute(lambda _: fake.email())
    ...
```

Each sub-app has its own `tests/` directory with:
- `test_models.py` — Model constraints, validation, methods
- `test_services.py` — Business logic unit tests
- `test_selectors.py` — Query logic tests
- `test_api.py` — DRF endpoint integration tests (status codes, payloads, permissions)
- `factories.py` — factory_boy factories

## Step 9: OpenAPI Documentation

drf-spectacular auto-generates OpenAPI 3.0 schema from DRF views.
Add `@extend_schema()` decorators for custom docs:

```python
from drf_spectacular.utils import extend_schema

class UserViewSet(viewsets.ModelViewSet):
    @extend_schema(
        summary="List users",
        responses={200: UserSerializer(many=True)},
        tags=["users"],
    )
    def list(self, request): ...
```

## Step 10: Docker & Tooling

### Dockerfile (multi-stage with uv)
```dockerfile
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable
COPY . .
RUN uv run manage.py collectstatic --noinput

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application"]
```

### docker-compose.yml
- PostgreSQL 16, Redis 7, Mailhog

### Makefile
```makefile
.PHONY: run test lint format migrate shell createsuperuser generate-schema run-prod

run:
	uv run manage.py runserver

run-prod:
	uv run gunicorn config.wsgi:application

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

migrate:
	uv run manage.py migrate

makemigrations:
	uv run manage.py makemigrations

shell:
	uv run manage.py shell_plus  # django-extensions

createsuperuser:
	uv run manage.py createsuperuser

generate-schema:
	uv run manage.py spectacular --file api/schema.yaml
```

### pyproject.toml tool config
```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["tests.py", "test_*.py"]
addopts = "-v --tb=short --strict-markers"

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "DJ"]

[tool.mypy]
plugins = ["mypy_django_plugin.main", "mypy_drf_plugin.main"]
python_version = "3.12"
strict = true
```

### .env.example
```bash
# Django
DJANGO_SETTINGS_MODULE=config.settings.development
SECRET_KEY=change-me-in-production
DATABASE_URL=postgres://postgres:postgres@localhost:5432/$0

# CORS (production only — comma-separated)
CORS_ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com

# Sentry (production only)
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.1

# AWS S3 (production only — for file storage)
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1

# Redis
REDIS_URL=redis://localhost:6379/0
```

## Step 11: Documentation

- `README.md` with: purpose, architecture diagram, setup, run, test, API docs URL
- `docs/adr/` with ADR template
- `.github/pull_request_template.md`

## Rules
- ALWAYS create a custom User model from day one (never use default `auth.User`)
- Business logic in `services.py` / `selectors.py`, NEVER in views or serializers
- Each sub-app is independently testable with its own factories + tests
- Sub-apps within a bounded context may import from each other
- Bounded contexts MUST NOT import from each other directly (use events/signals)
- All API responses use consistent envelope via custom renderer
- Use type hints everywhere (Python 3.12+ syntax: `list[str]`, `str | None`)
- Use `ruff` for linting + formatting, `mypy` for type checking
- DRF ViewSets for CRUD, APIView for custom actions
- Always version APIs (`/api/v1/...`)
- Use `uv run` for ALL Python/Django commands
- `uv.lock` MUST be committed to version control
- CORS: strict allowlist in production, permissive only in development
- Gunicorn: always use `gunicorn.conf.py`, never inline flags
- WhiteNoise handles static files — no need for nginx in simple deployments
- Sentry: never send PII (`send_default_pii=False`)
