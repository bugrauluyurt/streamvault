# StreamVault

FastAPI starter project with async SQLAlchemy, using astral.sh's toolchain (uv, ruff, ty).

## Prerequisites

- Python 3.13.5+
- [uv](https://docs.astral.sh/uv/) - Package manager
- [Docker](https://www.docker.com/) - For PostgreSQL

## Quick Start

1. **Copy environment file**

```bash
cp .env.example .env
```

2. **Install dependencies**

```bash
make install
```

3. **Start PostgreSQL**

```bash
make db-up
```

4. **Run migrations**

```bash
make upgrade
```

5. **Start the development server**

```bash
make dev
```

The API will be available at http://localhost:8000

API docs: http://localhost:8000/docs

## Development Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies with uv |
| `make dev` | Run FastAPI with hot-reload |
| `make db-up` | Start PostgreSQL container |
| `make db-down` | Stop PostgreSQL container |
| `make up` | Full startup (db + migrations + dev) |

### Code Quality

| Command | Description |
|---------|-------------|
| `make lint` | Run ruff linter with auto-fix |
| `make format` | Format code with ruff |
| `make typecheck` | Run ty type checker |
| `make check` | Run all checks (format + lint + typecheck) |

### Testing

| Command | Description |
|---------|-------------|
| `make test` | Run tests with pytest |
| `make test-cov` | Run tests with coverage report |

### Database

| Command | Description |
|---------|-------------|
| `make migrate msg="description"` | Create new Alembic migration |
| `make upgrade` | Apply pending migrations |
| `make downgrade` | Rollback last migration |

## Project Structure

```
streamvault/
├── app/
│   ├── core/           # Configuration and database setup
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── routers/        # API endpoints
│   ├── services/       # Business logic
│   └── migrations/     # Alembic migrations
├── tests/              # Test suite
├── docker-compose.yml  # PostgreSQL service
├── Makefile            # Development commands
└── pyproject.toml      # Project configuration
```

## Tech Stack

- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **SQLAlchemy** - Async ORM
- **Alembic** - Database migrations
- **PostgreSQL** - Database
- **uv** - Package manager
- **ruff** - Linter and formatter
- **ty** - Type checker
- **pytest** - Testing framework
