from pydantic import BaseModel, validator
import datetime


class HourlyBitcoinPriceSchema(BaseModel):
    unix_timestamp: int
    high: float
    low: float
    open: float
    close: float
    volumefrom: float
    volumeto: float

    # # Ensure timestamp is after 2022-01-01
    # @validator("unix_timestamp")
    # def validate_unix_timestamp(cls, value):
    #     min_timestamp = int(datetime.datetime(2022, 1, 1).timestamp())
    #     if value < min_timestamp:
    #         raise ValueError(
    #             f"Timestamp must be after {datetime.datetime(2022,1,1).isoformat()}"
    #         )
    #     return value

    class Config:
        orm_mode = True
