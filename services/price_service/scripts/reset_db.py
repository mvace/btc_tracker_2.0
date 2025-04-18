import asyncio
from app.database import engine
from app.models import Base


async def reset():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


asyncio.run(reset())
