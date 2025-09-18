# pages/3_📈_Portfolio_Detail.py

import streamlit as st
import pandas as pd
import plotly.express as px
import requests  # Import the requests library to make HTTP calls
from streamlit_cookies_manager import EncryptedCookieManager


cookies = EncryptedCookieManager(
    password="my_secret_encryption_password",
)
if not cookies.ready():
    # This is a temporary state while the browser initializes, so we stop and rerun.
    st.stop()

jwt_token = cookies.get("jwt_token")
# --- Configuration ---
# IMPORTANT: Update this URL to point to your running FastAPI backend
API_URL = "https://bitfolio.up.railway.app"

# --- API Calling Functions (defined directly in this file) ---


def get_portfolios(token: str):
    """Fetches all portfolios for the logged-in user."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/portfolio/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        # You can add more sophisticated error handling here
        st.error(f"Error fetching portfolios: {response.status_code}")
        return []


def get_transactions_for_portfolio(token: str, portfolio_id: int):
    """Fetches all transactions for a specific portfolio."""
    headers = {"Authorization": f"Bearer {token}"}
    # This endpoint URL is an example, adjust it to your API's actual URL structure
    response = requests.get(
        f"{API_URL}/transaction/{portfolio_id}/transactions/", headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching transactions: {response.status_code}")
        return []

