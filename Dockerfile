FROM python:3.13-slim AS builder

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

RUN uv run playwright install chromium --with-deps

COPY app/ ./app/
COPY alembic.ini ./

RUN uv sync --frozen --no-dev

FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN playwright install-deps chromium && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/app ./app
COPY --from=builder /app/alembic.ini ./
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PYTHONPATH="/app"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["api"]
