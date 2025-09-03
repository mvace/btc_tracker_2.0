import asyncio
from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, User, Portfolio, Transaction
from core.settings import settings
from passlib.context import CryptContext

# ----- Settings -----
DATABASE_URL = settings.db_url
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ----- Create engine and session -----
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# ----- Helper to create hashed password -----
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def populate():
    async with async_session() as session:
        async with session.begin():
            # # Optional: clear all tables first
            # await session.execute("DELETE FROM transactions")
            # await session.execute("DELETE FROM portfolios")
            # await session.execute("DELETE FROM users")

            # ---- Create users ----
            users_data = [
                {"email": "alice@example.com", "password": "alicepass"},
                {"email": "bob@example.com", "password": "bobpass"},
                {"email": "carol@example.com", "password": "carolpass"},
            ]

            users = []
            for u in users_data:
                user = User(
                    email=u["email"],
                    password_hash=hash_password(u["password"]),
                    created_at=datetime.utcnow(),
                )
                users.append(user)
                session.add(user)

            await session.flush()  # get user IDs

            # ---- Create portfolios ----
            portfolios = []
            for i, user in enumerate(users):
                for j in range(2):  # 2 portfolios per user
                    p = Portfolio(
                        name=f"{user.email.split('@')[0]}_portfolio_{j+1}",
                        user_id=user.id,
                    )
                    portfolios.append(p)
                    session.add(p)

            await session.flush()  # get portfolio IDs

            # ---- Create transactions ----
            transactions = []
            for p in portfolios:
                for k in range(3):  # 3 transactions per portfolio
                    t = Transaction(
                        portfolio_id=p.id,
                        btc_amount=Decimal("0.01") * (k + 1),
                        price_at_purchase=Decimal("30000.00") + k * 1000,
                        initial_value_usd=Decimal("0.01")
                        * (k + 1)
                        * (Decimal("30000.00") + k * 1000),
                        timestamp_hour_rounded=datetime.utcnow(),
                    )
                    transactions.append(t)
                    session.add(t)

        # Commit all changes
        await session.commit()
        print("Database populated successfully!")


if __name__ == "__main__":
    asyncio.run(populate())
