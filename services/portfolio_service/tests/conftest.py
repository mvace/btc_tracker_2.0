import pytest
import asyncio
from typing import AsyncGenerator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from core.settings import settings

# --- 1. Create a separate, asynchronous engine for the test database ---
test_engine = create_async_engine(settings.db_url_test, pool_pre_ping=True)

# --- 2. Create a sessionmaker for the test database ---
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# --- 3. A fixture to set up and tear down the database for a test session ---
@pytest.fixture(scope="session")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # Before the tests run, create all the tables in the test database.
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Yield a session to be used by the dependency override.
    async with TestingSessionLocal() as session:
        yield session

    # After the tests are done, drop the tables again.
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# --- 4. The main fixture that every test will use ---
@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    The primary fixture for testing. It provides a clean database and an
    HTTP client for making requests to the application.
    """

    # --- This is the dependency override magic ---
    # This function will replace the original get_db dependency in your app.
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    # Apply the override.
    app.dependency_overrides[get_db] = override_get_db

    # Create an async HTTP client that talks to your app.
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Clean up the override after the test is done.
    del app.dependency_overrides[get_db]
