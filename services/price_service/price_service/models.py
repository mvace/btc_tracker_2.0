from sqlalchemy import Column, Integer, BigInteger, Float
from price_service.price_service.database import Base
from pydantic import BaseModel
from typing import List


class HourlyBitcoinPrice(Base):
    __tablename__ = "hourly_bitcoin_prices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    unix_timestamp = Column(BigInteger, index=True, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volumefrom = Column(Float, nullable=False)
    volumeto = Column(Float, nullable=False)
