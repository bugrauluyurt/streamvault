# StreamVault

A streaming service data aggregator that scrapes, validates, and stores movie and TV show information from platforms like JustWatch. Uses LLM-powered extraction (via Ollama) and TMDB for data validation and enrichment.

## Prerequisites

- Python 3.13.5+
- [uv](https://docs.astral.sh/uv/) - Package manager
- [Docker](https://www.docker.com/) - For PostgreSQL

## Local Development

### Option A: Native Development (Recommended for active development)

Run the application directly on your machine with hot-reload:

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Install dependencies
make install

# 3. Install Playwright browsers (for scraping)
make playwright-install

# 4. Start PostgreSQL
make db-up

# 5. Run migrations
make upgrade

# 6. Start the API server (Terminal 1)
make dev

# 7. Start workers (Terminal 2)
make worker
```

### Option B: Docker Development (Full containerized setup)

Run everything in Docker with hot-reload:

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start all services (db + api + worker)
make docker-dev

# View logs
make docker-dev-logs

# Stop services
make docker-dev-down
```

The API will be available at http://localhost:8000

API docs: http://localhost:8000/docs

## Development Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies with uv |
| `make dev` | Run FastAPI with hot-reload |
| `make worker` | Start background job workers |
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
| `make hooks-install` | Install pre-commit hooks |
| `make hooks-uninstall` | Uninstall pre-commit hooks |

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

### Docker

| Command | Description |
|---------|-------------|
| `make docker-build` | Build Docker images |
| `make docker-up` | Start all containers (production mode) |
| `make docker-down` | Stop all containers |
| `make docker-logs` | Follow logs from all containers |
| `make docker-logs-api` | Follow API container logs |
| `make docker-logs-worker` | Follow worker container logs |
| `make docker-dev` | Start dev environment with hot-reload |
| `make docker-dev-down` | Stop dev environment |
| `make docker-dev-logs` | Follow dev environment logs |
| `make logs-up` | Start logging stack (Loki + Grafana) |
| `make logs-up-dev` | Start logging stack for dev environment |
| `make logs-ui` | Open Grafana UI in browser |

## Project Structure

```
streamvault/
├── app/
│   ├── core/           # Configuration and database setup
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── routers/        # API endpoints
│   ├── services/       # Business logic
│   ├── workers/        # Background job workers
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
- **LangChain** - LLM orchestration
- **Ollama** - Local LLM runtime
- **Playwright** - Browser automation

## Ollama Setup

StreamVault requires an external Ollama instance for LLM-powered data extraction. Ollama runs separately on the host machine (not in Docker).

### Installation

Install Ollama from [ollama.com](https://ollama.com) and pull the required model:

```bash
ollama pull qwen3:30b
```

### Configuration

Set the Ollama endpoint in your `.env` file:

```bash
# Local Ollama (production)
OLLAMA_HOST=http://localhost:11434

# Remote Ollama (development)
OLLAMA_HOST=http://10.0.0.139:11434
```

## Environment Variables

All configuration is done via environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `postgres` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `POSTGRES_DB` | `streamvault` | Database name |
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `qwen3:30b` | Default model for extraction |
| `TMDB_API_KEY` | - | TMDB API key (required for TMDB routes) |
| `QUEUE_WORKERS` | `2` | Number of worker tasks per process |
| `QUEUE_POLL_INTERVAL` | `1.0` | Seconds between queue polls |
| `SHARED_DIR` | `/app/data/shared` | Shared storage directory |

## API Endpoints

### Scrape Routes (`/scraped`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/scraped/popular` | Scrape popular shows from a URL |
| POST | `/scraped/top-ten` | Scrape top 10 movies and series |

### Shows Routes (`/shows`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/shows/scraped` | Get paginated list of scraped shows |
| GET | `/shows/scraped/top-ten` | Get top 10 movies and series from latest batch |
| GET | `/shows/scraped/{id}` | Get a single scraped show by ID |

### Jobs Routes (`/jobs`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/jobs` | Enqueue a new background job |
| GET | `/jobs` | List jobs (with optional status filter) |
| GET | `/jobs/{id}` | Get job status and result |
| POST | `/jobs/{id}/retry` | Retry a failed job |

### TMDB Routes (`/tmdb`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tmdb/search/movies` | Search TMDB for movies by query |
| GET | `/tmdb/search/tv` | Search TMDB for TV series by query |

## API Examples

### Scrape Endpoints

**Scrape popular shows:**
```bash
curl -X POST http://localhost:8000/scraped/popular \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.justwatch.com/us/movies",
    "origin": "justwatch",
    "max_items": 10,
    "download_tile_images": false,
    "download_cast_images": false,
    "download_background_images": false
  }'
```

**Scrape top 10:**
```bash
curl -X POST http://localhost:8000/scraped/top-ten \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "justwatch"
  }'
```

### Shows Endpoints

**Get paginated scraped shows:**
```bash
curl "http://localhost:8000/shows/scraped?skip=0&limit=20"
```

**Get top 10 movies and series:**
```bash
curl http://localhost:8000/shows/scraped/top-ten
```

**Get a single show by ID:**
```bash
curl http://localhost:8000/shows/scraped/1
```

### Jobs Endpoints

**Enqueue a scrape job:**
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "scrape_top_ten",
    "payload": {"origin": "justwatch"}
  }'
```

**Enqueue a popular scrape job:**
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "scrape_popular",
    "payload": {
      "origin": "justwatch",
      "url": "https://www.justwatch.com/us/movies"
    }
  }'
```

**Get job status:**
```bash
curl http://localhost:8000/jobs/1
```

**List pending jobs:**
```bash
curl "http://localhost:8000/jobs?status=pending"
```

**Retry a failed job:**
```bash
curl -X POST http://localhost:8000/jobs/1/retry
```

### TMDB Endpoints

**Search for movies:**
```bash
curl "http://localhost:8000/tmdb/search/movies?query=inception&page=1"
```

**Search for TV series:**
```bash
curl "http://localhost:8000/tmdb/search/tv?query=breaking%20bad&page=1"
```

**Search with details:**
```bash
curl "http://localhost:8000/tmdb/search/movies?query=inception&include_details=true"
```

## Background Job Queue

The application includes a PostgreSQL-based job queue for running long-running tasks in the background.

### Architecture

```
┌─────────────────┐     ┌─────────────────────┐
│   FastAPI API   │     │   Worker Process    │
│                 │     │                     │
│  POST /jobs ────┼──▶  │  ┌───────────────┐  │
│  GET /jobs/{id} │     │  │ Worker 1      │  │
│                 │     │  │ Worker 2      │  │
└────────┬────────┘     │  │ ...           │  │
         │              │  └───────────────┘  │
         ▼              │         │           │
    ┌─────────┐         │         ▼           │
    │ Postgres│◀────────┼── Poll & Process    │
    │  jobs   │         │                     │
    └─────────┘         └─────────────────────┘
```

### Running Workers

Workers run as a separate process from the API:

```bash
# Terminal 1: Start API
make dev

# Terminal 2: Start workers (default: 2 workers)
make worker

# Or with custom worker count
QUEUE_WORKERS=4 make worker
```

### Job Types

| Job Type | Description |
|----------|-------------|
| `scrape_top_ten` | Scrape top 10 movies and series |
| `scrape_popular` | Scrape popular shows from a URL |
| `validate_and_store` | Validate scraped data against TMDB and store |

### Queue Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `QUEUE_WORKERS` | `2` | Number of worker tasks per process |
| `QUEUE_POLL_INTERVAL` | `1.0` | Seconds between queue polls |

## Production Deployment

### Building and Running

```bash
# 1. Copy and configure environment
cp .env.example .env
# Edit .env with production values (strong passwords, real API keys, etc.)

# 2. Build production images
make docker-build

# 3. Start all services
make docker-up

# View logs
make docker-logs
```

### Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  streamvault-api│  │streamvault-worker│  │streamvault-db│ │
│  │    (FastAPI)    │  │  (Job Workers)   │  │ (PostgreSQL) │ │
│  │   Port: 8000    │  │                  │  │  Port: 5432  │ │
│  └────────┬────────┘  └────────┬─────────┘  └──────┬──────┘ │
│           │                    │                    │        │
│           └────────────────────┴────────────────────┘        │
│                              │                               │
│                    ┌─────────▼─────────┐                    │
│                    │  ./data/postgres  │ (DB persistence)   │
│                    │  ./data/shared    │ (Images/files)     │
│                    └───────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

### Container Details

| Container | Description | Network Mode |
|-----------|-------------|--------------|
| `streamvault-api` | FastAPI application server | host |
| `streamvault-worker` | Background job workers | host |
| `streamvault-db` | PostgreSQL 16 database | bridge (port 5432) |

### Data Persistence

| Volume | Path | Purpose |
|--------|------|---------|
| `./data/postgres` | `/var/lib/postgresql/data` | Database files |
| `./data/shared` | `/app/data/shared` | Downloaded images, scraped files |

### Production Environment Variables

Create a `.env` file with production values:

```bash
# Database (use strong passwords in production)
POSTGRES_USER=streamvault
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=streamvault
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Ollama LLM
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:30b

# External APIs
TMDB_API_KEY=<your-tmdb-api-key>

# Worker Configuration
QUEUE_WORKERS=4
QUEUE_POLL_INTERVAL=1.0

# Storage
SHARED_DIR=/app/data/shared
```

### Stopping Services

```bash
# Stop all containers
make docker-down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Centralized Logging

The project includes a centralized logging stack using Loki and Grafana for log aggregation, persistence, and visualization.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Logging Stack                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   Promtail  │───▶│    Loki     │◀───│      Grafana        │  │
│  │ (collector) │    │  (storage)  │    │       (UI)          │  │
│  └──────┬──────┘    │ Port: 3100  │    │    Port: 3001       │  │
│         │           └─────────────┘    └─────────────────────┘  │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Docker Container Logs                       │    │
│  │   streamvault-api  |  streamvault-worker  |  postgres   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Starting the Logging Stack

```bash
# Start logging services (without restarting existing containers)
make logs-up-dev    # For development
make logs-up        # For production

# Open Grafana UI
make logs-ui        # Opens http://localhost:3001
```

### Accessing Logs

1. Open Grafana at http://localhost:3001
2. Go to **Explore** (compass icon in sidebar)
3. Select **Loki** as the datasource
4. Use LogQL queries to filter logs

### LogQL Query Examples

| Query | Description |
|-------|-------------|
| `{container_name="streamvault-api-dev"}` | All API logs |
| `{container_name="streamvault-worker-dev"}` | All worker logs |
| `{container_name=~"streamvault.*"}` | All StreamVault logs |
| `{service="api"} \|= "ERROR"` | API errors |
| `{service="worker"} \|= "job"` | Worker job-related logs |
| `{container_name=~"streamvault.*"} \|~ "(?i)error"` | Case-insensitive error search |

### Log Retention

Logs are retained for **14 days** by default. This can be configured in `docker/loki/loki-config.yml`:

```yaml
limits_config:
  retention_period: 336h  # 14 days
```

### Data Persistence

| Volume | Path | Purpose |
|--------|------|---------|
| `./data/loki` | `/loki` | Log storage and indexes |
| `./data/grafana` | `/var/lib/grafana` | Grafana dashboards and settings |
