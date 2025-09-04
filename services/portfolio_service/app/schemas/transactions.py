from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class TransactionCreate(BaseModel):
    portfolio_id: int
    btc_amount: Decimal
    timestamp: datetime


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
