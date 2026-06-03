---
name: init-fastapi
description: Scaffold a new FastAPI project with clean architecture, async patterns, and TDD using uv. Use when creating a new FastAPI backend service.
argument-hint: "[project-name]"
disable-model-invocation: true
---

# Initialize FastAPI Project

Scaffold a production-grade FastAPI project for: **$ARGUMENTS**

## Step 1: Project Generation with uv

```bash
uv init $0 && cd $0
```

### Add dependencies:

```bash
# Framework
uv add fastapi "uvicorn[standard]"

# Database
uv add sqlalchemy "asyncpg" alembic

# Validation & serialization
uv add pydantic pydantic-settings

# Auth
uv add "python-jose[cryptography]" passlib "bcrypt"

# Observability
uv add structlog sentry-sdk

# HTTP client
uv add httpx

# Dev & test
uv add --group dev ruff mypy ipython
uv add --group test pytest pytest-asyncio pytest-cov httpx factory-boy faker
```

### Generate project structure:

```bash
mkdir -p src/$0/{api/v1,core,domain,infrastructure,tests}
touch src/$0/__init__.py
```

## Step 2: Project Structure

```
$0/
├── src/
│   └── $0/
│       ├── __init__.py
│       ├── main.py                    # FastAPI app factory
│       ├── config.py                  # Pydantic Settings
│       │
│       ├── core/                      # Cross-cutting concerns
│       │   ├── __init__.py
│       │   ├── database.py            # SQLAlchemy async engine & session
│       │   ├── dependencies.py        # Shared FastAPI dependencies
│       │   ├── exceptions.py          # Custom exception handlers
│       │   ├── middleware.py          # CORS, request ID, logging
│       │   └── security.py           # JWT, password hashing
│       │
│       ├── domain/                    # Business logic (no framework deps)
│       │   └── <feature>/
│       │       ├── __init__.py
│       │       ├── models.py          # SQLAlchemy models
│       │       ├── schemas.py         # Pydantic schemas (request/response)
│       │       ├── service.py         # Business logic
│       │       ├── repository.py      # Data access (async)
│       │       └── exceptions.py      # Domain-specific errors
│       │
│       ├── api/                       # Transport layer
│       │   ├── __init__.py
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py          # Aggregate router
│       │       └── <feature>/
│       │           ├── __init__.py
│       │           ├── endpoints.py   # Route handlers
│       │           └── dependencies.py # Route-specific deps
│       │
│       └── infrastructure/            # External integrations
│           ├── __init__.py
│           └── clients/               # External API clients
│
├── alembic/                           # DB migrations
│   ├── env.py
│   └── versions/
├── alembic.ini
│
├── tests/
│   ├── conftest.py                    # Fixtures: async client, test DB
│   ├── test_health.py
│   └── domain/
│       └── <feature>/
│           ├── test_service.py
│           └── test_endpoints.py
│
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── .env.example
```

## Step 3: Core Implementation

### main.py — App Factory
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .core.database import engine
from .core.exceptions import register_exception_handlers
from .api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await engine.dispose()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    register_exception_handlers(app)

    # Routes
    app.include_router(api_router, prefix="/api/v1")

    return app

app = create_app()
```

### config.py — Pydantic Settings
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "$0"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/$0"

    # Auth
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Sentry
    SENTRY_DSN: str = ""

settings = Settings()
```

### database.py — Async SQLAlchemy
```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Dependency Injection Pattern
```python
# domain/orders/service.py
class OrderService:
    def __init__(self, db: AsyncSession, repo: OrderRepository):
        self.db = db
        self.repo = repo

    async def create_order(self, data: CreateOrderSchema) -> Order:
        order = Order(**data.model_dump())
        self.db.add(order)
        await self.db.flush()
        return order

# api/v1/orders/dependencies.py
async def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    repo = OrderRepository(db)
    return OrderService(db, repo)

# api/v1/orders/endpoints.py
@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    data: CreateOrderRequest,
    service: OrderService = Depends(get_order_service),
):
    return await service.create_order(data)
```

## Step 4: Test Infrastructure

### conftest.py
```python
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.app.main import create_app
from src.app.core.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def client(db_session):
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
```

## Step 5: Tooling

### Makefile
```makefile
run:
	uv run uvicorn src.$0.main:app --reload
run-prod:
	uv run uvicorn src.$0.main:app --host 0.0.0.0 --port 8000 --workers 4
test:
	uv run pytest -v
lint:
	uv run ruff check . && uv run mypy src/
format:
	uv run ruff format .
migrate:
	uv run alembic upgrade head
migration:
	uv run alembic revision --autogenerate -m "$(msg)"
```

## Rules
- Use `async` everywhere — async endpoints, async SQLAlchemy, async httpx
- Pydantic schemas for ALL request/response validation
- Dependency injection via FastAPI `Depends()` — never import DB sessions directly
- Business logic in `service.py`, not in endpoints
- Use Alembic for migrations, never `Base.metadata.create_all` in production
- All commands via `uv run`
- Type hints everywhere (Python 3.12+)
