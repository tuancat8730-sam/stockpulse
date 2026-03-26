"""Shared pytest fixtures for all test suites.

DB isolation strategy: each test runs inside its own session transaction
which is rolled back at the end — no persistent test data.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

# ---------------------------------------------------------------------------
# Database URL
# ---------------------------------------------------------------------------
_RAW_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://stockpulse:stockpulse_dev@localhost:5433/stockpulse",
    ),
)


def _to_asyncpg(url: str) -> str:
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return url.replace(prefix, "postgresql+asyncpg://", 1)
    return url


TEST_DATABASE_URL = _to_asyncpg(_RAW_URL)


# ---------------------------------------------------------------------------
# Engine — NullPool means a fresh connection per fixture, no pool pollution
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def db_engine():
    # NullPool: each connect() call creates a new connection,
    # ensuring no cross-test state leaks in asyncpg.
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    yield engine
    await engine.dispose()


# ---------------------------------------------------------------------------
# Per-test session with automatic rollback
# ---------------------------------------------------------------------------

@pytest.fixture()
async def db_session(db_engine) -> AsyncSession:
    """AsyncSession whose transaction is rolled back after each test."""
    async with AsyncSession(db_engine, expire_on_commit=False) as session:
        await session.begin()
        yield session
        await session.rollback()
