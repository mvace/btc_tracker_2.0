from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Portfolio, User
from app.schemas.portfolios import PortfolioRead
from core.security import get_current_user
from fastapi import HTTPException

router = APIRouter()


@router.get("/", response_model=list[PortfolioRead])
async def list_transactions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    query = select(Portfolio).where(Portfolio.user_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{portfolio_id}", response_model=PortfolioRead)
async def get_portfolio(
    portfolio_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    query = select(Portfolio).where(
        Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id
    )
    result = await db.execute(query)
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio
