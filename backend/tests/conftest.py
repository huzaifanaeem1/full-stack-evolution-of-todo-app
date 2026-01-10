import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.src.main import app
from backend.src.config.database import get_db_session
from backend.src.models.user import User
from backend.src.models.task import Task
from backend.src.models import SQLModel
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """Create a test database session"""
    # Create an in-memory SQLite database for testing
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"

    # Create async engine for testing
    test_async_engine = create_async_engine(DATABASE_URL)
    test_async_session = async_sessionmaker(test_async_engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    async with test_async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Yield the session
    async with test_async_session() as session:
        yield session

    # Close the engine after tests
    await test_async_engine.dispose()


@pytest.fixture(scope="function")
def override_get_db_session(db_session):
    """Override the get_db_session dependency with the test session"""
    async def _get_db_session():
        yield db_session
    return _get_db_session


@pytest.fixture(scope="function")
async def test_client(override_get_db_session):
    """Create a test client with overridden database dependency"""
    app.dependency_overrides[get_db_session] = override_get_db_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()