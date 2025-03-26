from sqlalchemy import Column, Integer, BigInteger, Float
from app.database import Base
from sqlalchemy import CheckConstraint


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
    __table_args__ = (
        CheckConstraint("unix_timestamp >= 1279328400", name="valid_unix_timestamp"),
    )
