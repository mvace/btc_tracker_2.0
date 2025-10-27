from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, Any
from pydantic import field_validator
from utils.timestamp import get_last_valid_timestamp, FIRST_HISTORICAL_TIMESTAMP
from pydantic_core.core_schema import ValidationInfo
from pydantic import BaseModel, model_validator
from typing import Self


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
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        last_valid_timestamp = get_last_valid_timestamp()
        if not FIRST_HISTORICAL_TIMESTAMP < v <= last_valid_timestamp:
            raise ValueError(
                f"Timestamp is out of the valid range. Last valid is timestamp is {last_valid_timestamp}."
            )
        return v


class TransactionRead(BaseModel):
    id: int
    portfolio_id: int
    btc_amount: Decimal
    btc_price: Decimal = Field(alias="price_at_purchase")
    initial_value_usd: Decimal
    timestamp_hour_rounded: datetime
    model_config = {"from_attributes": True, "populate_by_name": True}


class TransactionReadWithMetrics(TransactionRead):
    current_value_usd: Decimal | None = None
    net_result: Decimal | None = None
    roi: Decimal | None = None

    @model_validator(mode="after")
    def calculate_metrics(self, info: ValidationInfo) -> Self:
        if self.current_value_usd is not None:
            return self

        current_price = info.context.get("current_price")
        if current_price is None:
            raise ValueError(
                "`current_price` must be provided in the validation context."
            )
        self.current_value_usd = self.btc_amount * current_price
        if self.initial_value_usd > 0:
            self.net_result = self.current_value_usd - self.initial_value_usd
            self.roi = self.net_result / self.initial_value_usd
        else:
            self.net_result = Decimal("0.0")
            self.roi = Decimal("0.0")
        return self


class PriceData(BaseModel):
    unix_timestamp: int
    high: Decimal
    low: Decimal
    open: Decimal
    close: Decimal
    volumefrom: Decimal
    volumeto: Decimal
