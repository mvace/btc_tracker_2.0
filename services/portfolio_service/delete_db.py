from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from core.settings import settings
from passlib.context import CryptContext
import asyncio
from sqlalchemy import text  # Import text

# ----- Settings -----
DATABASE_URL = settings.db_url
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ----- Create engine and session -----
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def delete():
    async with async_session() as session:
        async with session.begin():
            # # Optional: clear all tables first
            await session.execute(text("DELETE FROM transactions"))
            await session.execute(text("DELETE FROM portfolios"))
            await session.execute(text("DELETE FROM users"))


if __name__ == "__main__":
    asyncio.run(delete())
