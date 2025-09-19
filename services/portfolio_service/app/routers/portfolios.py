from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import Portfolio, Transaction, User
from app.schemas.portfolios import (
    PortfolioRead,
    PortfolioCreate,
    PortfolioReadWithMetrics,
)
from core.security import get_current_user
from fastapi import HTTPException, status
from decimal import Decimal

router = APIRouter()


@router.get("/", response_model=list[PortfolioRead])
async def list_portfolios(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    query = select(Portfolio).where(Portfolio.user_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{portfolio_id}", response_model=PortfolioReadWithMetrics)
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

    metrics_query = select(
        func.sum(Transaction.btc_amount).label("total_btc_amount"),
        func.sum(Transaction.initial_value_usd).label("total_initial_value"),
    ).where(Transaction.portfolio_id == portfolio_id)
    metrics_result = await db.execute(metrics_query)
    metrics = metrics_result.one()
    # total_btc = metrics.total_btc or Decimal("0.0")
    initial_value = metrics.total_initial_value or Decimal("0.0")
    btc_amount = metrics.total_btc_amount or Decimal("0.0")

    return PortfolioReadWithMetrics(
        id=portfolio.id,
        name=portfolio.name,
        initial_value_usd=initial_value,
        total_btc_amount=btc_amount,
    )


@router.post("/", response_model=PortfolioRead, status_code=201)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Portfolio:

    new_portfolio = Portfolio(name=portfolio_data.name, user_id=current_user.id)
    db.add(new_portfolio)
    try:
        await db.commit()
        await db.refresh(new_portfolio)
    except IntegrityError:
        # This block will run if the UniqueConstraint is violated
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A portfolio with this name already exists",
        )
    return new_portfolio


@router.put("/{portfolio_id}", response_model=PortfolioRead)
async def update_portfolio(
    portfolio_id: int,
    portfolio_data: PortfolioCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Portfolio:
    query = select(Portfolio).where(
        Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id
    )
    result = await db.execute(query)
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    portfolio.name = portfolio_data.name
    try:
        await db.commit()
        await db.refresh(portfolio)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A portfolio with this name already exists",
        )
    return portfolio


@router.delete("/{portfolio_id}", status_code=204)
async def delete_portfolio(
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

    await db.delete(portfolio)
    await db.commit()
    return
