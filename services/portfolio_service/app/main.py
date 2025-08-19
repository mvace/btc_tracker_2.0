from fastapi import FastAPI
from app.routers import portfolios, transactions
from core.settings import settings


app = FastAPI(title="Portfolio Microservice")

app.include_router(portfolios.router, prefix="/portfolios", tags=["Portfolios"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "env": settings.APP_ENV}
