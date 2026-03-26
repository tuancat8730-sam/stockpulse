"""FastAPI application entry point.

Lifespan initialises the DB engine and tears it down cleanly on shutdown.
Full lifespan (Redis, bot webhook, APScheduler) is wired in Task 0.5.1.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.config import get_settings
from app.core.database import close_db, init_db
from app.routers.auth import router as auth_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    init_db(settings.database_url)
    logger.info("Database initialised")
    yield
    await close_db()
    logger.info("Database closed")


app = FastAPI(
    title="StockPulse VN",
    description="Vietnamese stock market Telegram bot API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
