import requests
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

cookies = EncryptedCookieManager(
    password="my_secret_encryption_password",
)
if not cookies.ready():
    st.stop()

API_URL = st.secrets["API_URL"]


def get_token():
    """Retrieves the JWT token from the cookie."""
    return cookies.get("jwt_token")


def login_user(username, password):
    """Function to log in a user and get a JWT token."""
    try:
        response = requests.post(
            f"{API_URL}/auth/token", data={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            cookies["jwt_token"] = data.get("access_token")
            return True

        else:

            st.error(f"Login failed: {response.json().get('detail')}")
            return False
    except requests.exceptions.ConnectionError as e:
        st.error(
            f"Connection Error: Could not connect to the API. Is the backend running? Details: {e}"
        )

        return False


def logout_user():
    """Function to log out a user."""
    cookies["jwt_token"] = ""
