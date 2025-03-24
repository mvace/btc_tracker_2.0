from fastapi import APIRouter, HTTPException, Depends
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import HourlyBitcoinPrice
from app.schemas import HourlyBitcoinPriceSchema
from app.database import get_db
from app.utils.timestamp import round_timestamp_to_nearest_hour


router = APIRouter()


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
    """Rounds the timestamp to the nearest full hour and returns the Bitcoin price for that hour."""

    # Round timestamp
    rounded_timestamp = round_timestamp_to_nearest_hour(unix_timestamp)

    # Get min and max timestamp from DB
    min_result = await db.execute(
        select(HourlyBitcoinPrice.unix_timestamp)
        .order_by(HourlyBitcoinPrice.unix_timestamp.asc())
        .limit(1)
    )
    max_result = await db.execute(
        select(HourlyBitcoinPrice.unix_timestamp)
        .order_by(HourlyBitcoinPrice.unix_timestamp.desc())
        .limit(1)
    )

    min_ts = min_result.scalar() - 1800
    max_ts = max_result.scalar() + 1799

    # Validate timestamp range
    if min_ts is None or max_ts is None:
        raise HTTPException(
            status_code=500, detail="No price data available in the database."
        )
    if not (min_ts <= rounded_timestamp <= max_ts):
        raise HTTPException(
            status_code=400,
            detail=f"Timestamp out of valid range. Must be between {min_ts} and {max_ts}.",
        )

    # Fetch price
    result = await db.execute(
        select(HourlyBitcoinPrice).where(
            HourlyBitcoinPrice.unix_timestamp == rounded_timestamp
        )
    )
    price = result.scalars().first()
    if price is None:
        raise HTTPException(status_code=404, detail="Price record not found")
    return price
