from fastapi import APIRouter, HTTPException, Depends
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import HourlyBitcoinPrice
from app.schemas import HourlyBitcoinPriceSchema
from app.database import SessionLocal
from app.utils.timestamp import round_timestamp_to_nearest_hour
from typing import List

router = APIRouter()


# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        yield session


# Get all Bitcoin prices
@router.get("/", response_model=Page[HourlyBitcoinPriceSchema])
async def get_all_prices(db: AsyncSession = Depends(get_db)):
    """Returns paginated hourly Bitcoin prices sorted by timestamp DESC."""
    return await paginate(
        db, select(HourlyBitcoinPrice).order_by(desc(HourlyBitcoinPrice.unix_timestamp))
    )


add_pagination(router)  # Enables pagination globally


# Get a specific Bitcoin price by Unix timestamp
@router.get("/{unix_timestamp}", response_model=HourlyBitcoinPriceSchema)
async def get_price_by_timestamp(
    unix_timestamp: int, db: AsyncSession = Depends(get_db)
):
    """Rounds the timestamp to the nearest full hour and returns the Bitcoin price for a the Unix timestamp of that nearest hour."""
    rounded_timestamp = round_timestamp_to_nearest_hour(unix_timestamp)

    result = await db.execute(
        select(HourlyBitcoinPrice).where(
            HourlyBitcoinPrice.unix_timestamp == rounded_timestamp
        )
    )
    price = result.scalars().first()
    if price is None:
        raise HTTPException(status_code=404, detail="Price record not found")
    return price
