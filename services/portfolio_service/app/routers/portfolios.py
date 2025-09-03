from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import models
from app.schemas.portfolios import PortfolioRead

router = APIRouter()


@router.get("/", response_model=list[PortfolioRead])
async def list_portfolios(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Portfolio))
    return result.scalars().all()
