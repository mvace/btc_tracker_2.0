from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from collections.abc import AsyncGenerator
from core.settings import settings

DATABASE_URL = settings.db_url
APP_ENV = settings.APP_ENV

# Create async engine
engine = create_async_engine(
    DATABASE_URL, echo=(settings.APP_ENV == "development"), pool_pre_ping=True
)

# Create async session
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


# Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
