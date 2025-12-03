from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import health, scrape


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield


app = FastAPI(
    title="StreamVault",
    description="FastAPI starter project with async SQLAlchemy",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(scrape.router)
