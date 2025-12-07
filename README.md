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

## LLM Setup (Ollama)

The project includes Ollama for local LLM inference with GPU support. Two profiles are available:
- `nvidia` - For NVIDIA GPUs (RTX 5080, etc.)
- `amd` - For AMD GPUs (7900 XTX, etc.) using ROCm

### Prerequisites

**NVIDIA GPU:**
```bash
# Install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

**AMD GPU:**
```bash
# Install ROCm (Ubuntu 22.04+)
sudo apt install rocm-hip-libraries
sudo usermod -a -G video,render $USER
# Logout and login for group changes
```

### Starting Ollama

```bash
# For NVIDIA GPU
make ollama-nvidia

# For AMD GPU
make ollama-amd

# Stop Ollama
make ollama-down
```

Models are automatically pulled on first startup (qwen2.5:7b and llama3.2:3b by default).

### Installing Playwright

```bash
make playwright-install
```

### LLM Commands

| Command | Description |
|---------|-------------|
| `make ollama-nvidia` | Start Ollama with NVIDIA GPU |
| `make ollama-amd` | Start Ollama with AMD GPU (ROCm) |
| `make ollama-down` | Stop Ollama container |
| `make playwright-install` | Install Playwright browsers |

### Usage Example

```python
from pydantic import BaseModel, Field
from app.services.scraper_service import ScraperService

class ProductData(BaseModel):
    title: str = Field(description="Product title")
    price: float = Field(description="Price in USD")
    availability: str = Field(description="In stock or out of stock")

scraper = ScraperService()
product = await scraper.extract_data(
    url="https://example.com/product/123",
    schema=ProductData,
)
print(product.title, product.price)
```

### Configuration

Environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Default model for extraction |
| `OLLAMA_MODELS` | `qwen2.5:7b,llama3.2:3b` | Models to pre-pull on startup |

## API Endpoints

### Scrape Routes (`/scrape`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/scrape/popular` | Scrape popular shows from a URL |
| POST | `/scrape/top-ten` | Scrape top 10 movies and series |

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

## API Examples

### Scrape Endpoints

**Scrape popular shows:**
```bash
curl -X POST http://localhost:8000/scrape/popular \
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
curl -X POST http://localhost:8000/scrape/top-ten \
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
| `enrich_tmdb` | Enrich show data with TMDB info (future) |

### Queue Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `QUEUE_WORKERS` | `2` | Number of worker tasks per process |
| `QUEUE_POLL_INTERVAL` | `1.0` | Seconds between queue polls |
