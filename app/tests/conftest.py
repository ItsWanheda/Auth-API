"""Pytest fixtures: isolated DB session and FastAPI test client."""

from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator, Iterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Override env BEFORE importing app modules.
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-32-chars-minimum-1234"
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/authapi_test",
)
os.environ.setdefault(
    "DATABASE_URL_SYNC",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/authapi_test",
)

from app.config.settings import get_settings  # noqa: E402
get_settings.cache_clear()  # reload with test env

from app.core.database import Base  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _create_schema() -> AsyncGenerator[None, None]:
    """Create the schema once per session; drop after."""
    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _truncate_tables() -> AsyncGenerator[None, None]:
    yield  # In real test setup, add truncation here per-test.


@pytest_asyncio.fixture()
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        yield session