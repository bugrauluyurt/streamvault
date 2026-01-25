.PHONY: install up down logs check lint format typecheck test test-cov migrate upgrade downgrade hooks-install hooks-uninstall playwright-install api worker scheduler

# =============================================================================
# Main Commands
# =============================================================================

up: ## Start everything (Docker + native services)
	docker compose up -d
	@echo "Waiting for database..."
	@sleep 3
	uv run alembic upgrade head
	@echo "Starting native services..."
	@nohup uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/streamvault-api.log 2>&1 &
	@nohup uv run python -m app.workers.cli > /tmp/streamvault-worker.log 2>&1 &
	@nohup uv run python -m app.workers.scheduler_cli > /tmp/streamvault-scheduler.log 2>&1 &
	@sleep 2
	@echo "All services started!"
	@echo "API: http://localhost:8000"
	@echo "Grafana: http://localhost:3001"
	@echo "Logs: /tmp/streamvault-*.log"

down: ## Stop everything
	-pkill -f "uvicorn app.main" 2>/dev/null || true
	-pkill -f "app.workers.cli" 2>/dev/null || true
	-pkill -f "app.workers.scheduler_cli" 2>/dev/null || true
	docker compose down

logs: ## Follow Docker logs
	docker compose logs -f

status: ## Show running services
	@echo "=== Docker ===" && docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(NAME|streamvault)" || true
	@echo ""
	@echo "=== Native ===" && ps aux | grep -E "(uvicorn|workers)" | grep -v grep || echo "No native services running"

# =============================================================================
# Native Services
# =============================================================================

api: ## Run API server
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

api-dev: ## Run API with hot-reload
	uv run uvicorn app.main:app --reload

worker: ## Run background workers
	uv run python -m app.workers.cli

scheduler: ## Run scheduler
	uv run python -m app.workers.scheduler_cli

# =============================================================================
# Database
# =============================================================================

db-up: ## Start only PostgreSQL
	docker compose up -d db

migrate: ## Create migration (usage: make migrate msg="description")
	uv run alembic revision --autogenerate -m "$(msg)"

upgrade: ## Apply pending migrations
	uv run alembic upgrade head

downgrade: ## Rollback last migration
	uv run alembic downgrade -1

# =============================================================================
# Code Quality
# =============================================================================

install: ## Install Python dependencies
	uv sync

check: format lint typecheck ## Run all checks

lint: ## Run linter with auto-fix
	uv run ruff check --fix .

format: ## Format code
	uv run ruff format .

typecheck: ## Run type checker
	uv run ty check

# =============================================================================
# Testing
# =============================================================================

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov=app --cov-report=html

# =============================================================================
# Setup
# =============================================================================

hooks-install: ## Install pre-commit hooks
	uv run pre-commit install

hooks-uninstall: ## Uninstall pre-commit hooks
	uv run pre-commit uninstall

playwright-install: ## Install Playwright browsers
	uv run playwright install chromium

# =============================================================================
# Logs UI
# =============================================================================

logs-ui: ## Open Grafana in browser
	@echo "Opening http://localhost:3001"
	@command -v open >/dev/null && open http://localhost:3001 || echo "Visit http://localhost:3001"

# =============================================================================
# Help
# =============================================================================

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
