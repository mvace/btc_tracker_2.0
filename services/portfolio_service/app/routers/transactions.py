from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Transaction, User, Portfolio
from app.schemas.transactions import TransactionRead
from core.security import get_current_user
from fastapi import HTTPException

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
