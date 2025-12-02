.PHONY: install dev db-up db-down lint format typecheck check test test-cov migrate upgrade downgrade up hooks-install hooks-uninstall ollama-nvidia ollama-amd ollama-down playwright-install

install:
	uv sync

dev:
	uv run uvicorn app.main:app --reload

db-up:
	docker-compose up -d db

db-down:
	docker-compose down db

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

ollama-nvidia:
	docker-compose --profile nvidia up -d ollama

ollama-amd:
	docker-compose --profile amd up -d ollama-amd

ollama-down:
	docker-compose --profile nvidia --profile amd down ollama ollama-amd 2>/dev/null || true

playwright-install:
	uv run playwright install chromium
