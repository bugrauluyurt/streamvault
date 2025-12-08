#!/bin/bash
set -e

echo "Waiting for database..."
while ! python -c "
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os

async def check():
    url = f\"postgresql+asyncpg://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}\"
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        await conn.execute(text('SELECT 1'))
    await engine.dispose()

asyncio.run(check())
" 2>/dev/null; do
    echo "Database not ready, waiting..."
    sleep 2
done
echo "Database is ready"

echo "Running migrations..."
alembic upgrade head

case "$1" in
    api)
        echo "Starting API server..."
        exec uvicorn app.main:app --host 0.0.0.0 --port 8000
        ;;
    worker)
        echo "Starting ${QUEUE_WORKERS:-2} worker(s)..."
        exec python -m app.workers.cli
        ;;
    scheduler)
        echo "Starting scheduler..."
        exec python -m app.workers.scheduler_cli
        ;;
    *)
        exec "$@"
        ;;
esac
