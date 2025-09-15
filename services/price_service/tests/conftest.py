import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from httpx import AsyncClient
from httpx import ASGITransport

# Create async SQLite engine
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine_test = create_async_engine(DATABASE_URL, future=True, echo=False)
TestSessionLocal = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


# Dependency override
async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="module", autouse=True)
async def prepare_test_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def db_session():
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


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
