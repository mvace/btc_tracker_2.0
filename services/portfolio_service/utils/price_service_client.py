import httpx  # Import httpx
import logging  # Import logging
from pydantic import ValidationError
from app.schemas.transactions import PriceData
from core.settings import settings

# It's a good practice to set up a logger
logger = logging.getLogger(__name__)


async def fetch_btc_price_data_for_timestamp(timestamp: int) -> PriceData | None:
    """
    Fetches the historical Bitcoin price in USD for a given timestamp from the price_service API.
    Returns PriceData on success, or None on failure.
    """
    url = f"{settings.PRICE_SERVICE_BASE_URL}/prices/{timestamp}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)

            response.raise_for_status()

            return PriceData(**response.json())

    except httpx.RequestError as exc:
        logger.error(
            f"An error occurred while requesting price data from {exc.request.url!r}: {exc}"
        )
        return None

    except httpx.HTTPStatusError as exc:
        logger.error(
            f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc.response.text}"
        )
        return None

    except ValidationError as exc:
        logger.error(f"Failed to validate price data from API: {exc}")
        return None
