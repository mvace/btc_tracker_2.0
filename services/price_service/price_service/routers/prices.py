from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from price_service.price_service.models import HourlyBitcoinPrice
from price_service.price_service.schemas import HourlyBitcoinPriceSchema
from price_service.price_service.database import SessionLocal
from typing import List

router = APIRouter()


# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        yield session


# Get all Bitcoin prices
@router.get("/", response_model=List[HourlyBitcoinPriceSchema])
async def get_all_prices(db: AsyncSession = Depends(get_db)):
    """Returns the full list of hourly Bitcoin prices from the database."""
    result = await db.execute(select(HourlyBitcoinPrice))
    if result is None:
        raise HTTPException(status_code=404, detail="No records found")
    prices = result.scalars().all()
    return prices


# Get a specific Bitcoin price by Unix timestamp
@router.get("/{unix_timestamp}", response_model=HourlyBitcoinPriceSchema)
async def get_price_by_timestamp(
    unix_timestamp: int, db: AsyncSession = Depends(get_db)
):
    """Returns the Bitcoin price for a specific Unix timestamp."""
    result = await db.execute(
        select(HourlyBitcoinPrice).where(
            HourlyBitcoinPrice.unix_timestamp == unix_timestamp
        )
    )
    price = result.scalars().first()
    if price is None:
        raise HTTPException(status_code=404, detail="Price record not found")
    return price
