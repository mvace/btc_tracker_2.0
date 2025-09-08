from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    UniqueConstraint,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Numeric, BigInteger, Integer

from app.database import Base

# ---- Decimal precisions ----
# BTC amounts need up to 8 decimal places
NUM_BTC = Numeric(20, 8)
# Fiat prices and values with 2 decimal places
NUM_USD = Numeric(20, 2)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    # Store only the password hash (never plaintext). Hashing/verification is done in auth layer.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    portfolios: Mapped[list["Portfolio"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Ownership
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # Mandatory human-friendly name
    name: Mapped[str | None] = mapped_column(String(100), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="portfolios")
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="portfolio", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("name", "user_id", name="_user_portfolio_name_uc"),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # Amount of BTC purchased (positive, up to 8 decimals)
    btc_amount: Mapped[Decimal] = mapped_column(NUM_BTC, nullable=False)

    # Price at purchase (USD) returned by price_service for the rounded hour
    price_at_purchase: Mapped[Decimal] = mapped_column(NUM_USD, nullable=False)

    # Initial value in USD at time of purchase (btc_amount * price_at_purchase)
    initial_value_usd: Mapped[Decimal] = mapped_column(NUM_USD, nullable=False)

    # The rounded hour in **UTC** used to fetch price (tz-aware)
    timestamp_hour_rounded: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship(back_populates="transactions")
