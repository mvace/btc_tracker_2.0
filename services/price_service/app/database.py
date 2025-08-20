from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.settings import ASYNC_DATABASE_URL
from collections.abc import AsyncGenerator


DATABASE_URL = ASYNC_DATABASE_URL

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


# Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
