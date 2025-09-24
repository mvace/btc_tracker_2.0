from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, func, case
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
from utils.fetch_current_btc_price import get_current_price

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
    # The efficient query remains the same
    query = (
        select(
            Portfolio.id.label("id"),
            Portfolio.name.label("name"),
            # 1. Coalesce SUM to 0 if no transactions exist (returns NULL)
            func.coalesce(func.sum(Transaction.initial_value_usd), 0).label(
                "initial_value_usd"
            ),
            func.coalesce(func.sum(Transaction.btc_amount), 0).label(
                "total_btc_amount"
            ),
            # 2. Use a CASE statement to prevent division by zero for average_price
            case(
                (
                    func.sum(Transaction.btc_amount) > 0,
                    func.sum(Transaction.btc_amount * Transaction.price_at_purchase)
                    / func.sum(Transaction.btc_amount),
                ),
                else_=0,
            ).label("average_price_usd"),
        )
        # 3. Use a LEFT JOIN (isouter=True) to include portfolios with no transactions
        .join(
            Transaction,
            Portfolio.id == Transaction.portfolio_id,
            isouter=True,
        )
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
        .group_by(Portfolio.id, Portfolio.name)
    )

    result = await db.execute(query)
    data = result.one_or_none()

    # Fail fast: check for data immediately after the query
    if not data:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Get external data (e.g., from a live price feed API)
    current_price = get_current_price()

    # The model now handles all calculations.
    # We unpack the database row and pass the current_price.
    # data._asdict() converts the SQLAlchemy Row object to a dictionary.
    return PortfolioReadWithMetrics.model_validate(
        data, from_attributes=True, context={"current_price": current_price}
    )


@router.post("/", response_model=PortfolioRead, status_code=201)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Portfolio:

    new_portfolio = Portfolio(
        name=portfolio_data.name,
        goal_in_usd=portfolio_data.goal_in_usd,
        user_id=current_user.id,
    )
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
