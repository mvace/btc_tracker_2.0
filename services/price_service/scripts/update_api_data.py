import requests
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.models import HourlyBitcoinPrice
from app.utils.timestamp import round_timestamp_down_to_hour
import asyncio
from datetime import datetime, timezone
import time


async def get_last_hourly_bitcoin_data():
    async with SessionLocal() as session:
        result = await session.execute(
            select(HourlyBitcoinPrice).order_by(HourlyBitcoinPrice.id.desc()).limit(1)
        )

        return result.scalars().first()


async def save_hourly_bitcoin_data(session: AsyncSession, data: dict):
    new_entry = HourlyBitcoinPrice(
        unix_timestamp=data["time"],
        high=data["high"],
        low=data["low"],
        open=data["open"],
        close=data["close"],
        volumefrom=data["volumefrom"],
        volumeto=data["volumeto"],
    )
    session.add(new_entry)
    await session.commit()


async def fetch_and_save_bitcoin_price():
    async with SessionLocal() as session:
        # Get the latest record from the database and calculate how many records is missing for the latest record till now and use it as limit parameter
        latest_record = await get_last_hourly_bitcoin_data()
        latest_record_ts = latest_record.unix_timestamp
        current_ts = int(time.time())
        current_ts_rounded_down = round_timestamp_down_to_hour(current_ts)
        limit = (current_ts - latest_record_ts) // 3600 - 1

        # Make the API request
        response = requests.get(
            "https://min-api.cryptocompare.com/data/v2/histohour",
            params={"fsym": "BTC", "tsym": "USD", "limit": {limit}},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

        # Get the data in json format
        json_response = response.json()
        data = json_response["Data"]["Data"]

        # Loop over the records and save it to db
        for record in data:
            # Skip the latest input from "current hour" as the columns close, low and high might still change
            if record["time"] == current_ts_rounded_down:
                continue
            await save_hourly_bitcoin_data(session=session, data=record)


# Run inside an async event loop
async def main():
    await fetch_and_save_bitcoin_price()
    print("Done")


asyncio.run(main())
