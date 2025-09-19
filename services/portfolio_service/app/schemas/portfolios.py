from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class PortfolioRead(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class PortfolioReadWithMetrics(PortfolioRead):
    initial_value_usd: Decimal = Field(
        description="Total USD value of all transactions at the time of purchase."
    )
    total_btc_amount: Decimal = Field(
        description="Total BTC amount of all transactions in the portfolio"
    )
