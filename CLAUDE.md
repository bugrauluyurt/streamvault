# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
make install           # Install dependencies with uv
make dev               # Run FastAPI with hot-reload on :8000
make up                # Full startup: db + migrations + dev server
make db-up             # Start PostgreSQL container
make db-down           # Stop PostgreSQL container
make upgrade           # Apply pending Alembic migrations
make downgrade         # Rollback last migration
make migrate msg="x"   # Create new auto-generated migration
make check             # Run all checks: format + lint + typecheck
make lint              # Run ruff linter with auto-fix
make format            # Format code with ruff
make typecheck         # Run ty type checker
make test              # Run pytest
make test-cov          # Run pytest with coverage report
make playwright-install # Install Playwright browsers
make worker            # Start background job workers
make hooks-install     # Install pre-commit hooks
make hooks-uninstall   # Uninstall pre-commit hooks
```

## Architecture

FastAPI application with async SQLAlchemy for streaming service data management.

```
app/
├── main.py              # FastAPI app entry point with lifespan
├── core/
│   ├── config.py        # Pydantic Settings (env vars)
│   └── database.py      # Async SQLAlchemy engine + session factory
├── models/              # SQLAlchemy ORM models (async, 2.0 style)
├── schemas/             # Pydantic validation schemas
├── routers/             # FastAPI route handlers
├── services/            # Business logic
├── workers/             # Background job workers and handlers
├── enums/               # Type enumerations (JobType, JobStatus, etc.)
└── migrations/          # Alembic database migrations
```

**Database**: Async SQLAlchemy 2.0 with asyncpg driver. Use `get_db()` dependency for sessions.

**Services**:
- `LLMService`: LangChain + Ollama for structured data extraction
- `ScraperService`: Playwright browser automation + LLM extraction
- `QueueService`: PostgreSQL-based job queue management
- `ShowsService`: Scraped show data queries
- `TMDBService`: TMDB API integration for movie/TV search

## Code Style

- Python 3.13.5+, package manager: `uv`
- Linter/formatter: ruff (line-length: 100)
- Type checker: ty (pyright-based)
- Pre-commit runs `make check` before commits
- Use `type` instead of `interface` pattern (Pydantic models)
- Relative imports within app/
- JSONB for complex nested data (images, cast, audio/subtitles)

## Testing

```bash
make test              # Run all tests
pytest tests/test_health.py::test_health_check  # Run single test
```

Uses pytest-asyncio with auto mode. Test fixtures in `tests/conftest.py`.

## Before Completing Tasks

Always run `make check` (lint + typecheck) before finishing any task.
