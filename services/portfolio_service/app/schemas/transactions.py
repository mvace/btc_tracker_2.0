from pydantic import BaseModel
from datetime import datetime


class TransactionCreate(BaseModel):
    portfolio_id: int
    btc_amount: float
    timestamp: datetime


class TransactionRead(BaseModel):
    id: int
    portfolio_id: int
    btc_amount: float
    btc_price: float
    initial_value_usd: float
    timestamp: datetime
    model_config = {"from_attributes": True}
