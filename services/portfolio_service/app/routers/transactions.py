from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import models
from app.schemas.transactions import TransactionRead

router = APIRouter()


# @router.get("/")
# async def list_transactions(db: Session = Depends(get_db)):
#     return db.query(models.Transaction).all()


@router.get("/", response_model=list[TransactionRead])
async def list_transactions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Transaction))
    return result.scalars().all()
