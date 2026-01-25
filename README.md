![StreamVault](assets/streamvault_logo_wide.png)

A streaming service data aggregator that scrapes, validates, and stores movie and TV show information from platforms like JustWatch. Uses LLM-powered extraction (via Ollama) and TMDB for data validation and enrichment.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) - Package manager
- [Docker](https://www.docker.com/) - For PostgreSQL, Loki, Grafana

## Quick Start

```bash
# 1. Copy environment file and configure
cp .env.example .env
# Edit .env with your TMDB_API_KEY and OLLAMA_HOST

# 2. Install dependencies
make install

# 3. Install Playwright browsers (for scraping)
make playwright-install

# 4. Start everything
make up
```

This starts:
- **Docker**: PostgreSQL, Loki, Promtail, Grafana
- **Native**: API server, Workers, Scheduler

The API will be available at http://localhost:8000

API docs: http://localhost:8000/docs

Grafana (logs): http://localhost:3001

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Docker                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Postgres │  │   Loki   │  │ Promtail │  │ Grafana  │   │
│  │  :5432   │  │  :3100   │  │          │  │  :3001   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     Native (Python)                         │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐                 │
│  │   API    │  │ Workers  │  │ Scheduler │                 │
│  │  :8000   │  │  (2x)    │  │  (cron)   │                 │
│  └──────────┘  └──────────┘  └───────────┘                 │
└─────────────────────────────────────────────────────────────┘

                          │
                          ▼
              ┌───────────────────────┐
              │   Ollama (external)   │
              │   :11434              │
              └───────────────────────┘
```

## Commands

### Main

| Command        | Description                           |
| -------------- | ------------------------------------- |
| `make up`      | Start everything (Docker + native)    |
| `make down`    | Stop everything                       |
| `make status`  | Show running services                 |
| `make logs`    | Follow Docker logs                    |

### Native Services

| Command          | Description                     |
| ---------------- | ------------------------------- |
| `make api`       | Run API server                  |
| `make api-dev`   | Run API with hot-reload         |
| `make worker`    | Start background workers        |
| `make scheduler` | Start scheduler                 |

### Database

| Command                          | Description                  |
| -------------------------------- | ---------------------------- |
| `make db-up`                     | Start only PostgreSQL        |
| `make upgrade`                   | Apply pending migrations     |
| `make downgrade`                 | Rollback last migration      |
| `make migrate msg="description"` | Create new migration         |

### Code Quality

| Command        | Description                                |
| -------------- | ------------------------------------------ |
| `make check`   | Run all checks (format + lint + typecheck) |
| `make lint`    | Run ruff linter with auto-fix              |
| `make format`  | Format code with ruff                      |
| `make typecheck` | Run type checker                         |

### Testing

| Command         | Description                    |
| --------------- | ------------------------------ |
| `make test`     | Run tests                      |
| `make test-cov` | Run tests with coverage        |

### Setup

| Command                  | Description                    |
| ------------------------ | ------------------------------ |
| `make install`           | Install dependencies           |
| `make playwright-install`| Install Playwright browsers    |
| `make hooks-install`     | Install pre-commit hooks       |

## Configuration

Key environment variables in `.env`:

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=streamvault

# LLM
LLM_PROVIDER=ollama
OLLAMA_HOST=http://10.0.0.189:11434
OLLAMA_MODEL=qwen3-30b-40k:latest

# External APIs
TMDB_API_KEY=your_api_key_here

# Workers
QUEUE_WORKERS=2

# Storage
POSTGRES_DATA_DIR=/mnt/storage/streamvault/postgres
LOKI_DATA_DIR=/mnt/storage/streamvault/loki
GRAFANA_DATA_DIR=/mnt/storage/streamvault/grafana
```

## Scheduled Jobs

The scheduler runs these jobs automatically:

| Job                    | Schedule      | Description                    |
| ---------------------- | ------------- | ------------------------------ |
| scrape_top_ten         | 6:00, 15:00   | Scrape JustWatch top 10        |
| scrape_popular_movies  | 6:30, 15:30   | Scrape popular movies          |
| scrape_popular_series  | 7:00, 16:00   | Scrape popular TV shows        |
| validate_top_shows     | 7:30, 16:30   | Validate with TMDB + LLM       |
| validate_popular_shows | 8:00, 17:00   | Validate with TMDB + LLM       |

## API Endpoints

- `GET /health` - Health check
- `POST /jobs` - Create a job
- `GET /jobs` - List jobs
- `GET /jobs/{id}` - Get job status
- `GET /shows` - List validated shows
- `GET /scraped-shows` - List raw scraped data

## Project Structure

```
app/
├── main.py              # FastAPI entry point
├── core/
│   ├── config.py        # Settings (env vars)
│   └── database.py      # Async SQLAlchemy
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic schemas
├── routers/             # API routes
├── services/            # Business logic
│   ├── llm_service.py   # LLM abstraction
│   ├── scraper_service.py # Playwright scraping
│   ├── tmdb_service.py  # TMDB API client
│   └── queue_service.py # Job queue
└── workers/             # Background jobs
    ├── cli.py           # Worker CLI
    ├── scheduler_cli.py # Scheduler CLI
    └── handlers/        # Job handlers
```

## License

MIT
