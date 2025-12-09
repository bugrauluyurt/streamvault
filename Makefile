.PHONY: install dev db-up db-down lint format typecheck check test test-cov migrate upgrade downgrade up hooks-install hooks-uninstall playwright-install worker scheduler docker-build docker-build-tag docker-up docker-down docker-logs docker-logs-api docker-logs-worker docker-logs-scheduler docker-dev docker-dev-down docker-dev-logs logs-up logs-up-dev logs-ui docker-deploy docker-recreate docker-prune

# Generate timestamp tag for docker images
IMAGE_TAG ?= $(shell date +%Y%m%d-%H%M%S)

install:
	uv sync

dev:
	uv run uvicorn app.main:app --reload

db-up:
	docker compose up -d db

db-down:
	docker compose down db

lint:
	uv run ruff check --fix .

format:
	uv run ruff format .

typecheck:
	uv run ty check

check: format lint typecheck

test:
	uv run pytest

test-cov:
	uv run pytest --cov=app --cov-report=html

migrate:
	uv run alembic revision --autogenerate -m "$(msg)"

upgrade:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1

up: db-up upgrade dev

hooks-install:
	uv run pre-commit install

hooks-uninstall:
	uv run pre-commit uninstall

playwright-install:
	uv run playwright install chromium

worker:
	uv run python -m app.workers.cli

scheduler:
	uv run python -m app.workers.scheduler_cli

docker-build:
	IMAGE_TAG=latest docker compose build

docker-build-tag:
	IMAGE_TAG=$(IMAGE_TAG) docker compose build
	@echo "Built images with tag: $(IMAGE_TAG)"

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-logs-api:
	docker compose logs -f api

docker-logs-worker:
	docker compose logs -f worker

docker-logs-scheduler:
	docker compose logs -f scheduler

docker-dev:
	docker compose -f docker-compose.dev.yml up --build

docker-dev-down:
	docker compose -f docker-compose.dev.yml down

docker-dev-logs:
	docker compose -f docker-compose.dev.yml logs -f

logs-up:
	docker compose up -d loki promtail grafana

logs-up-dev:
	docker compose -f docker-compose.dev.yml up -d loki promtail grafana

logs-ui:
	open http://localhost:3001

docker-deploy:
	@if [ -z "$(TAG)" ]; then echo "Usage: make docker-deploy TAG=20251209-103045"; exit 1; fi
	IMAGE_TAG=$(TAG) docker compose up -d

docker-recreate:
	docker compose up -d --force-recreate

docker-prune:
	docker image prune -f
