import requests
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager


API_URL = st.secrets["API_URL"]

cookies = None  # will be set from main app


def set_cookie_manager(cookie_manager):
    global cookies
    cookies = cookie_manager


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


def register_user(user_data):
    try:
        response = requests.post(f"{API_URL}/auth/register", json=user_data)
        data = response.json()
        if response.status_code == 201:
            return 201, data
        else:
            return response.status_code, data

    except requests.exceptions.ConnectionError as e:
        return 503, {"detail": "Connection to the API failed."}
