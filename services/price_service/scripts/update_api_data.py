import requests
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.models import HourlyBitcoinPrice
from app.utils.timestamp import round_timestamp_down_to_hour
import asyncio
from datetime import datetime, timezone
import time
import aiohttp
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def get_last_hourly_bitcoin_data():
    async with SessionLocal() as session:
        result = await session.execute(
            select(HourlyBitcoinPrice)
            .order_by(HourlyBitcoinPrice.unix_timestamp.desc())
            .limit(1)
        )

        return result.scalars().first()


async def save_hourly_bitcoin_data(session: AsyncSession, data: dict):
    # Check if record already exists
    existing = await session.execute(
        select(HourlyBitcoinPrice).where(
            HourlyBitcoinPrice.unix_timestamp == data["time"]
        )
    )
    if existing.scalar_one_or_none():
        print(f"Skipping duplicate timestamp: {data['time']}")
        return

    new_entry = HourlyBitcoinPrice(
        unix_timestamp=data["time"],
        high=data["high"],
        low=data["low"],
        open=data["open"],
        close=data["close"],
        volumefrom=data["volumefrom"],
        volumeto=data["volumeto"],
    )
    print(f"Creating new entry for timestamp: {data['time']}")
    session.add(new_entry)
    await session.commit()


async def fetch_and_save_bitcoin_price():
    async with SessionLocal() as session:
        latest_record = await get_last_hourly_bitcoin_data()
        latest_record_ts = latest_record.unix_timestamp
        current_ts = int(time.time())
        current_ts_rounded_down = round_timestamp_down_to_hour(current_ts)

        total_hours = (current_ts_rounded_down - latest_record_ts) // 3600 - 1
        print(f"Total hours missing: {total_hours}")

        if total_hours <= 0:
            print("No new data to fetch.")
            return

        url = "https://min-api.cryptocompare.com/data/v2/histohour"
        all_data = []
        limit_per_request = 2000
        to_ts = current_ts_rounded_down

        async with aiohttp.ClientSession() as http_session:
            while total_hours > 0:
                limit = min(limit_per_request, total_hours)
                params = {"fsym": "BTC", "tsym": "USD", "limit": limit, "toTs": to_ts}

                async with http_session.get(url, params=params) as response:
                    if response.status != 200:
                        raise Exception(
                            f"API request failed with status {response.status}"
                        )
                    json_response = await response.json()

                    batch = json_response["Data"]["Data"]

                    # If the API returns fewer records than requested, stop
                    if not batch:
                        break

                    # If we expect more data after this batch, exclude last (toTs is inclusive)
                    if total_hours > limit:
                        all_data = batch[:-1] + all_data
                        earliest_ts = batch[0]["time"]
                        to_ts = earliest_ts - 1
                    else:
                        all_data = batch + all_data
                        break

                    total_hours -= limit

        # Save to DB
        for record in all_data:
            if record["time"] == current_ts_rounded_down:
                continue
            await save_hourly_bitcoin_data(session=session, data=record)


# Run inside an async event loop
async def main():
    await fetch_and_save_bitcoin_price()
    print("Done")


asyncio.run(main())
