from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Portfolio, User
from app.schemas.portfolios import PortfolioRead
from core.security import get_current_user

router = APIRouter()


@router.get("/", response_model=list[PortfolioRead])
async def list_transactions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    query = select(Portfolio).where(Portfolio.user_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()
