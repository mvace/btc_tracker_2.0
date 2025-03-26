from pydantic import BaseModel
import datetime


class HourlyBitcoinPriceSchema(BaseModel):
    unix_timestamp: int
    high: float
    low: float
    open: float
    close: float
    volumefrom: float
    volumeto: float

    class Config:
        orm_mode = True
