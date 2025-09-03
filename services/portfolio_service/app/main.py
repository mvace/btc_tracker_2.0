from fastapi import FastAPI
from app.routers import portfolios, transactions, auth
from core.settings import settings
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer


app = FastAPI(title="Portfolio Microservice")

app.include_router(portfolios.router, prefix="/portfolio", tags=["Portfolios"])
app.include_router(transactions.router, prefix="/transaction", tags=["Transactions"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "env": settings.APP_ENV}
