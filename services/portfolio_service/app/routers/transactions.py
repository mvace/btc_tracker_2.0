from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Transaction, User, Portfolio
from app.schemas.transactions import TransactionRead, TransactionCreate, PriceData
from core.security import get_current_user
from utils.price_service_client import fetch_btc_price_data_for_timestamp
from fastapi import HTTPException
import requests
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=list[TransactionRead])
async def list_transactions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Transaction).join(Portfolio).where(Portfolio.user_id == current_user.id)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=TransactionRead, status_code=201)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> TransactionRead:

    # Verify that the portfolio belongs to the current user
    query = select(Portfolio).where(
        Portfolio.id == transaction_data.portfolio_id,
        Portfolio.user_id == current_user.id,
    )
    result = await db.execute(query)
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    timestamp = int(transaction_data.timestamp.timestamp())
    price_data = await fetch_btc_price_data_for_timestamp(timestamp)

    btc_amount = transaction_data.btc_amount
    price_at_purchase = price_data.close
    initial_value_usd = btc_amount * price_at_purchase
    timestamp_hour_rounded = datetime.fromtimestamp(
        price_data.unix_timestamp, tz=timezone.utc
    )

    new_transaction = Transaction(
        portfolio_id=transaction_data.portfolio_id,
        btc_amount=btc_amount,
        price_at_purchase=price_at_purchase,
        initial_value_usd=initial_value_usd,
        timestamp_hour_rounded=timestamp_hour_rounded,
    )
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)
    return new_transaction


@router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction(
    transaction_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Transaction)
        .join(Portfolio)
        .where(
            Transaction.id == transaction_id,
            Portfolio.user_id == current_user.id,
        )
    )
    result = await db.execute(query)
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
