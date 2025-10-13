from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Transaction, User, Portfolio
from app.schemas.transactions import (
    TransactionRead,
    TransactionCreate,
    TransactionReadWithMetrics,
)
from core.security import get_current_user
from utils.price_service_client import fetch_btc_price_data_for_timestamp
from utils.fetch_current_btc_price import get_current_price
from fastapi import HTTPException
import requests
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=list[TransactionReadWithMetrics])
async def list_transactions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    portfolio_id: Optional[int] = Query(
        default=None, description="Filter transactions by portfolio ID"
    ),
):
    query = (
        select(
            Transaction.id,
            Transaction.portfolio_id,
            Transaction.btc_amount,
            Transaction.price_at_purchase,
            Transaction.btc_amount,
            Transaction.initial_value_usd,
            Transaction.timestamp_hour_rounded,
        )
        .join(Portfolio)
        .where(Portfolio.user_id == current_user.id)
    )
    if portfolio_id is not None:
        query = query.where(Transaction.portfolio_id == portfolio_id)

    result = await db.execute(query)
    data = result.all()
    if not data and portfolio_id:
        return []
    elif not data:
        raise HTTPException(
            status_code=404, detail="No transactions found for this user."
        )

    current_price = get_current_price()

    transactions_with_metrics = [
        TransactionReadWithMetrics.model_validate(
            transaction, from_attributes=True, context={"current_price": current_price}
        )
        for transaction in data
    ]

    return transactions_with_metrics


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

    if not price_data:
        raise HTTPException(
            status_code=503,  # Service Unavailable
            detail="Could not fetch price data from the external service. Please try again later.",
        )

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


@router.get("/{transaction_id}", response_model=TransactionReadWithMetrics)
async def get_transaction(
    transaction_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(
            Transaction.id,
            Transaction.portfolio_id,
            Transaction.btc_amount,
            Transaction.price_at_purchase,
            Transaction.btc_amount,
            Transaction.initial_value_usd,
            Transaction.timestamp_hour_rounded,
        )
        .join(Portfolio)
        .where(
            Transaction.id == transaction_id,
            Portfolio.user_id == current_user.id,
        )
    )
    result = await db.execute(query)
    data = result.one_or_none()

    if not data:
        raise HTTPException(status_code=404, detail="Transaction not found")

    current_price = get_current_price()

    transaction_with_metrics = TransactionReadWithMetrics.model_validate(
        data, from_attributes=True, context={"current_price": current_price}
    )
    return transaction_with_metrics


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
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

    await db.delete(transaction)
    await db.commit()
    return


@router.put("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> TransactionRead:
    # Verify that the transaction exists and belongs to the current user
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

    # Verify that the new portfolio (if changed) belongs to the current user
    if transaction.portfolio_id != transaction_data.portfolio_id:
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

    if not price_data:
        raise HTTPException(
            status_code=503,  # Service Unavailable
            detail="Could not fetch price data from the external service. Please try again later.",
        )

    btc_amount = transaction_data.btc_amount
    price_at_purchase = price_data.close
    initial_value_usd = btc_amount * price_at_purchase
    timestamp_hour_rounded = datetime.fromtimestamp(
        price_data.unix_timestamp, tz=timezone.utc
    )

    # Update transaction fields
    transaction.portfolio_id = transaction_data.portfolio_id
    transaction.btc_amount = btc_amount
    transaction.price_at_purchase = price_at_purchase
    transaction.initial_value_usd = initial_value_usd
    transaction.timestamp_hour_rounded = timestamp_hour_rounded

    await db.commit()
    await db.refresh(transaction)
    return transaction
