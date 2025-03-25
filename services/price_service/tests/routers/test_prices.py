from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.models import HourlyBitcoinPrice
from httpx import AsyncClient
from sqlalchemy import delete


DUMMY_TIMESTAMP = 1735689600


@pytest.fixture
async def test_price_entry(db_session):
    test_price = HourlyBitcoinPrice(
        unix_timestamp=DUMMY_TIMESTAMP,
        high=58000.0,
        low=57000.0,
        open=57500.0,
        close=57800.0,
        volumefrom=123.45,
        volumeto=7123456.78,
    )
    db_session.add(test_price)
    await db_session.commit()
    return test_price


@pytest.mark.anyio
async def test_get_data_by_timestamp_success(async_client, test_price_entry):
    response = await async_client.get(f"/prices/{test_price_entry.unix_timestamp}")
    assert response.status_code == 200
    data = response.json()
    assert data["close"] == 57800.0
    assert data["unix_timestamp"] == 1735689600


@pytest.mark.anyio
async def test_get_data_by_timestamp_not_found(async_client):
    nonexistent_timestamp = 1117062000
    response = await async_client.get(f"/prices/{nonexistent_timestamp}")
    assert response.status_code == 400
    assert "Timestamp out of valid range." in response.json()["detail"]


@pytest.mark.anyio
async def test_get_data_by_timestamp_invalid_input(async_client):
    response = await async_client.get("/prices/not-a-number")
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert (
        detail[0]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )


@pytest.mark.anyio
async def test_get_data_by_timestamp_rounds_to_existing(async_client, test_price_entry):
    nearby_ts = test_price_entry.unix_timestamp + 1000

    response = await async_client.get(f"/prices/{nearby_ts}")
    assert response.status_code == 200
    assert response.json()["unix_timestamp"] == test_price_entry.unix_timestamp


@pytest.mark.anyio
async def test_get_data_by_timestamp_below_min_timestamp(async_client):
    nonexistent_timestamp = 0
    response = await async_client.get(f"/prices/{nonexistent_timestamp}")
    assert response.status_code == 400
    assert "Timestamp out of valid range." in response.json()["detail"]


@pytest.mark.anyio
async def test_get_data_by_timestamp_above_max_timestamp(async_client):
    nonexistent_timestamp = 9999999999
    response = await async_client.get(f"/prices/{nonexistent_timestamp}")
    assert response.status_code == 400
    assert "Timestamp out of valid range." in response.json()["detail"]


@pytest.mark.anyio
async def test_get_data_by_timestamp_no_data_in_db(async_client, db_session):
    # Make sure there is no data in the table
    await db_session.execute(delete(HourlyBitcoinPrice))
    await db_session.commit()

    response = await async_client.get("/prices/1735689600")

    assert response.status_code == 500
    assert response.json()["detail"] == "No price data available in the database."
