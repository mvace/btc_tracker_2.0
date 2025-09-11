import httpx  # Import httpx
import logging  # Import logging
from pydantic import ValidationError
from app.schemas.transactions import PriceData

# It's a good practice to set up a logger
logger = logging.getLogger(__name__)


async def fetch_btc_price_data_for_timestamp(timestamp: int) -> PriceData | None:
    """
    Fetches the historical Bitcoin price in USD for a given timestamp from the price_service API.
    Returns PriceData on success, or None on failure.
    """
    url = (
        f"http://localhost:8000/prices/{timestamp}"  # Use service name if using Docker
    )

    try:
        # Use an async context manager for the client
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)  # Add a timeout

            # This will raise an httpx.HTTPStatusError for 4xx/5xx responses
            response.raise_for_status()

            # The Pydantic model will raise a ValidationError if the data is malformed
            return PriceData(**response.json())

    except httpx.RequestError as exc:
        # Catches connection errors, timeouts, etc.
        logger.error(
            f"An error occurred while requesting price data from {exc.request.url!r}: {exc}"
        )
        return None

    except httpx.HTTPStatusError as exc:
        # Catches 4xx and 5xx responses
        logger.error(
            f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc.response.text}"
        )
        return None

    except ValidationError as exc:
        # Catches errors if the response JSON doesn't match the PriceData schema
        logger.error(f"Failed to validate price data from API: {exc}")
        return None
