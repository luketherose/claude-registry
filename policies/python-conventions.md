# Python Conventions

This document defines the team's conventions for Python projects. These conventions
are enforced by the `developer-python` subagent.

---

## Technology baseline

| Component | Standard | Notes |
|-----------|----------|-------|
| Python | 3.12+ | Use type hints, match statements, exception groups |
| Package manager | `uv` (preferred) or `pip-tools` | Reproducible builds |
| Web framework | FastAPI 0.110+ | Async first; Pydantic v2 for models |
| ORM | SQLAlchemy 2.x | Async engine preferred for FastAPI |
| Validation | Pydantic v2 | All request/response models and config |
| Testing | pytest + pytest-asyncio + testcontainers-python | |
| Linting | Ruff | Replaces flake8, isort, and most pylint rules |
| Type checking | mypy (strict mode) | |
| Logging | structlog | JSON output in production |

---

## Project structure (FastAPI service)

```
src/
  {package}/
    __init__.py
    main.py                 — FastAPI app, lifespan, router registration
    api/
      v1/
        routers/
          {resource}.py     — APIRouter, endpoint definitions
        schemas/
          {resource}.py     — Pydantic request/response models
    service/
      {domain}_service.py   — Business logic, no HTTP concepts
    repository/
      {domain}_repository.py — SQLAlchemy queries, data access
    domain/
      models.py             — SQLAlchemy ORM models
      enums.py              — Domain enums
    config/
      settings.py           — pydantic-settings BaseSettings
    exceptions/
      base.py               — Base exception classes
      handlers.py           — FastAPI exception handlers
tests/
  unit/
    test_{module}.py
  integration/
    test_{feature}.py
pyproject.toml
uv.lock
```

---

## Mandatory rules

### Type hints
- All function signatures require type hints (parameters and return type)
- Use `from __future__ import annotations` for forward references in Python < 3.12
- `mypy --strict` must pass with zero errors in CI

### Pydantic models
- All request/response models are Pydantic `BaseModel` subclasses or `model_config = ConfigDict(...)`
- No raw `dict` as function arguments for validated data
- Use `model_validator` for cross-field validation

### Configuration
- All config in `pydantic_settings.BaseSettings`
- Environment variables for all secrets (never in code or `.env` files committed to git)
- `.env.example` committed (without values); `.env` gitignored

### Error handling
```python
# Base exception
class AppException(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 400):
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)

# FastAPI handler — RFC 7807 compatible
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "about:blank",
            "title": type(exc).__name__,
            "status": exc.status_code,
            "detail": str(exc),
            "errorCode": exc.error_code,
        }
    )
```

### Async
- Use `async def` for all FastAPI endpoint handlers
- Use `await` for all I/O operations
- Never call blocking I/O in async context — use `asyncio.to_thread()` if necessary
- Use `asyncpg` or async SQLAlchemy engine for DB access

### Logging (structlog)
```python
import structlog
log = structlog.get_logger()

# Use keyword arguments for structured context
log.info("order_created", order_id=order.id, customer_id=order.customer_id)

# Never log sensitive data
```

---

## Dependency management

```toml
# pyproject.toml — direct dependencies only, no pinned versions
[project]
dependencies = [
    "fastapi>=0.110",
    "pydantic>=2.6",
    "pydantic-settings>=2.2",
    "sqlalchemy>=2.0",
    "structlog>=24.1",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",   # for TestClient
    "mypy>=1.9",
    "ruff>=0.4",
]
```

Pin via `uv.lock` (committed to git). Regenerate with `uv lock`.

---

## Code quality gates (CI)

- `ruff check .` — zero errors
- `mypy --strict .` — zero errors
- `pytest --cov=src --cov-fail-under=70` — minimum coverage
