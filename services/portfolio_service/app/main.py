from fastapi import FastAPI
from app.routers import portfolios, transactions
from core.settings import settings
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer


app = FastAPI(title="Portfolio Microservice")

app.include_router(portfolios.router, prefix="/portfolios", tags=["Portfolios"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "env": settings.APP_ENV}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
