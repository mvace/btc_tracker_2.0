from fastapi import FastAPI
from app.routers import prices


app = FastAPI(title="Prices Microservice")

app.include_router(prices.router, prefix="/prices", tags=["Prices"])


@app.get("/")
def health_check():
    return {"status": "ok"}
