from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, Any
from pydantic import field_validator
from utils.timestamp import get_last_valid_timestamp, FIRST_HISTORICAL_TIMESTAMP


class TransactionCreate(BaseModel):
    portfolio_id: int
    btc_amount: Decimal = Field(
        gt=Decimal("0.00000000"),
        le=Decimal("21000000"),
        decimal_places=8,
        max_digits=16,
        description="Amount of BTC purchased (positive)",
    )

    timestamp: datetime = Field(
        gt=FIRST_HISTORICAL_TIMESTAMP,
        description="Timestamp of the transaction (UTC)",
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        last_valid_timestamp = get_last_valid_timestamp()
        if not FIRST_HISTORICAL_TIMESTAMP < v <= last_valid_timestamp:
            raise ValueError("Timestamp is out of the valid range.")
        return v


class TransactionRead(BaseModel):
    id: int
    portfolio_id: int
    btc_amount: Decimal
    btc_price: Decimal = Field(alias="price_at_purchase")
    initial_value_usd: Decimal
    timestamp_hour_rounded: datetime
    model_config = {"from_attributes": True, "populate_by_name": True}


class PriceData(BaseModel):
    unix_timestamp: int
    high: Decimal
    low: Decimal
    open: Decimal
    close: Decimal
    volumefrom: Decimal
    volumeto: Decimal


class TransactionRead(BaseModel):
    id: int
    portfolio_id: int
    btc_amount: Decimal
    btc_price: Decimal = Field(alias="price_at_purchase")
    initial_value_usd: Decimal
    timestamp_hour_rounded: datetime
    model_config = {"from_attributes": True, "populate_by_name": True}


class PriceData(BaseModel):
    unix_timestamp: int
    high: Decimal
    low: Decimal
    open: Decimal
    close: Decimal
    volumefrom: Decimal
    volumeto: Decimal
