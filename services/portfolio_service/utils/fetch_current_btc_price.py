from decimal import Decimal
import requests
from core.settings import settings

API_KEY = settings.CRYPTOCOMPARE_API_KEY


def get_current_price():
    """
    Fetches the current price of Bitcoin (BTC) in US Dollars (USD) from the CryptoCompare API.

    Uses the 'min-api.cryptocompare.com' endpoint to request the latest price of BTC in USD.
    Requires an API key set as an environment variable 'CRYPTOCOMPARE_API_KEY'.

    Returns:
    - Decimal: The current price of one Bitcoin in US Dollars.
    """
    endpoint = "https://min-api.cryptocompare.com/data/price"

    params = {
        "fsym": "BTC",  # From symbol (Bitcoin)
        "tsyms": "USD",  # To symbol (US Dollar)
        "api_key": API_KEY,
    }
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        data = response.json()

        if "USD" in data:
            current_price = Decimal(data["USD"]).quantize(
                Decimal("0.01")
            )  # Round to 2 decimal places
            return current_price
        else:
            print(f"Error: Unexpected response format: {data}")
            return None

    except requests.exceptions.RequestException as e:
        # Handle any requests-related errors (network issues, invalid responses, etc.)
        print(f"Error fetching data from CryptoCompare API: {e}")
        return None

    except (ValueError, KeyError) as e:
        # Handle JSON decoding errors or missing data in the response
        print(f"Error processing API response: {e}")
        return None


if __name__ == "__main__":
    price = get_current_price()
    if price is not None:
        print(f"Current BTC Price in USD: {price}")
    else:
        print("Failed to retrieve the current BTC price.")
