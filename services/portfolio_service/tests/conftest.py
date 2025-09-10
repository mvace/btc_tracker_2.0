import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.schemas.transactions import PriceData
from core.settings import settings

from faker import Faker
from fastapi import status


fake = Faker()


@pytest.fixture(scope="function")
async def created_user(client: AsyncClient) -> dict:
    """
    Creates a new user via the API for the purpose of a single test.

    Yields a dictionary containing the 'email' and 'password' of the created user.
    """
    user_data = {
        "email": fake.email(),
        "password": fake.password(),
    }

    # Use the `client` fixture to register the user
    response = await client.post("/auth/register", json=user_data)

    # Important assert: if user creation fails, the test
    # should fail immediately with a clear error.
    assert response.status_code == status.HTTP_201_CREATED

    # Yield the data to the test function
    yield user_data


@pytest.fixture(scope="function")
async def auth_headers(client: AsyncClient, created_user: dict) -> dict:
    """
    Logs in the created_user and yields authentication headers.
    """
    login_data = {
        "username": created_user["email"],
        "password": created_user["password"],
    }
    login_response = await client.post("/auth/token", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    yield headers


@pytest.fixture(scope="function")
async def created_portfolio(client: AsyncClient, auth_headers: dict) -> dict:
    """
    Creates a portfolio for the authenticated user and yields the portfolio data.
    """
    portfolio_data = {"name": "Test Portfolio"}
    create_response = await client.post(
        "/portfolio/", json=portfolio_data, headers=auth_headers
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    yield create_response.json()


@pytest.fixture(scope="function")
async def created_transaction(
    client: AsyncClient,
    auth_headers: dict,
    created_portfolio: dict,
    mocker,
) -> dict:
    """
    Creates a transaction for the authenticated user and yields the transaction data.
    MOCKS the external call to fetch BTC price data.
    """
    # 2. Define the fake data for the mock
    fake_price_data = PriceData(
        unix_timestamp=1756908000,
        high=112545.3,
        low=111143.27,
        open=111491.96,
        close=112293.52,
        volumefrom=2809.0,
        volumeto=314166893.0,
    )

    # 3. Patch the function to prevent the real network call
    mocker.patch(
        "app.routers.transactions.fetch_btc_price_data_for_timestamp",
        return_value=fake_price_data,
    )

    # 4. Now, the rest of your fixture will work without a real network call
    transaction_data = {
        "portfolio_id": created_portfolio["id"],
        "btc_amount": "0.01",
        "timestamp": "2023-10-01T12:00:00Z",
    }
    create_response = await client.post(
        "/transaction/", json=transaction_data, headers=auth_headers
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    yield create_response.json()


@pytest.fixture(scope="session")
def anyio_backend():
    """
    Forces all tests in the session to use the asyncio backend.
    This is an alternative way to enforce the backend if config files fail.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[any, None]:
    """
    Creates and disposes of the test database engine once per session.
    This manages the connection pool for the entire test run.
    """
    test_engine = create_async_engine(settings.DATABASE_URL_TEST)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a clean, isolated database for each test function.
    Creates tables, yields a transactional session, and then drops tables.
    """
    # Create a new sessionmaker bound to the session-scoped engine
    TestingSessionLocal = async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an AsyncClient with the database dependency overridden.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Use .clear() for a more robust cleanup
    app.dependency_overrides.clear()
