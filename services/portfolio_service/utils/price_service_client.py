import requests
from app.schemas.transactions import PriceData


async def fetch_btc_price_data_for_timestamp(timestamp: int) -> PriceData:
    """
    Fetches the historical Bitcoin price in USD for a given timestamp from the price_service API.
    """
    url = f"http://localhost:8000/prices/{timestamp}"
    response = requests.get(url)
    response.raise_for_status()
    return PriceData(**response.json())
