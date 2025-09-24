# streamlit_app.py
import streamlit as st
import requests
import pandas as pd
from streamlit_cookies_manager import EncryptedCookieManager

from decimal import Decimal
import plotly.graph_objects as go


# --- COOKIE MANAGER ---
cookies = EncryptedCookieManager(
    password="my_secret_encryption_password",
)
if not cookies.ready():
    st.stop()

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Bitcoin Portfolio Tracker", page_icon="💰", layout="wide"
)

API_URL = "https://bitfolio.up.railway.app"
# --- AUTHENTICATION & STATE ---

# Initialize session state variables if they don't exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = ""


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
    del cookies["jwt_token"]


def portfolio_list_view():
    """Display the list of all portfolios."""

    portfolio_response = requests.get(
        f"{API_URL}/portfolio/",
        headers={"Authorization": f"Bearer {jwt_token}"},
    )

    if portfolio_response.status_code == 200:
        portfolios = portfolio_response.json()
        st.header(f"You have {len(portfolios)} portfolios.")
        if not portfolios:
            st.info("You have no portfolios yet. Create one using the form below.")
        else:
            for portfolio in portfolios:
                col1, col2, col3 = st.columns([3, 3, 2])
                with col1:
                    st.write(f"**Portfolio ID:** {portfolio['id']}")
                with col2:
                    st.write(f"**Name:** {portfolio['name']}")
                with col3:
                    # CHANGE #1: Use st.button instead of st.link_button
                    # A unique key is crucial for buttons inside a loop.
                    if st.button("View Details", key=f"view_{portfolio['id']}"):
                        # Set the query parameter to the portfolio id
                        st.query_params["id"] = portfolio["id"]
                        st.rerun()
                st.divider()
    elif portfolio_response.status_code == 401:
        logout_user()
        st.rerun()
    else:
        st.error("Failed to retrieve portfolios.")


def portfolio_detail_view(portfolio_id: int):
    if st.button("← Back to all portfolios"):
        # Clear all query params to return to the list view
        st.query_params.clear()
        st.rerun()  # Optional: Explicitly rerun for immediate effect

    portfolio_response = requests.get(
        f"{API_URL}/portfolio/{portfolio_id}",
        headers={"Authorization": f"Bearer {jwt_token}"},
    )

    if portfolio_response.status_code == 200:
        portfolio = portfolio_response.json()

        st.header(f"Portfolio Overview: {portfolio['name'].replace('_', ' ').title()}")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            label="USD invested",
            value=f"${Decimal(portfolio['initial_value_usd']):,.0f}",
        )

        col2.metric(
            label="Current Value (USD)",
            value=f"${Decimal(portfolio['current_value_usd']):,.0f}",
        )

        col3.metric(
            label="Net P&L (USD)",
            value=f"${Decimal(portfolio['net_result']):,.0f}",
            delta=f"{Decimal(portfolio['roi']):.2%}",
        )

        col4, col5, col6 = st.columns(3)

        col4.metric(
            label="Average Price (USD)",
            value=f"${Decimal(portfolio['average_price_usd']):,.0f}",
        )

        col5.metric(
            label="ROI",
            value=f"{Decimal(portfolio['roi']):.2%}",
        )

        col6.metric(
            label="Total BTC Holdings",
            value=f"{Decimal(portfolio['total_btc_amount']):.8f} BTC",
        )
    elif portfolio_response.status_code == 401:
        logout_user()
        st.rerun()

    else:
        st.error("Portfolio not found.")


# --- UI ---

st.title("💰 Portfolio & Transaction Tracker")
jwt_token = cookies.get("jwt_token")

# If user is not logged in, show login/register forms
if not jwt_token:
    st.subheader("Welcome! Please log in or register.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        st.write("Or, try the app with a demo account:")
        if st.button("🚀 Use Demo Account"):
            # Use your existing login function with the demo credentials
            if login_user("bob@example.com", "bobpass"):
                st.rerun()

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if login_user(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()  # Rerun to hide the form and show the main app
    placeholder = st.empty()
    with register_tab:
        with st.form("register_form", clear_on_submit=True):
            st.write("Please fill in the details below to register.")

            email = st.text_input("Email")
            password = st.text_input(
                "Password",
                type="password",
                help="Password must be at least 8 characters long.",
            )
            confirm_password = st.text_input("Confirm Password", type="password")

            # The submit button for the form
            submitted = st.form_submit_button("Register")

    # --- Form Submission Logic ---
    if submitted:
        # 1. Client-side validation for a better user experience
        if not email or not password or not confirm_password:
            placeholder.error("⚠️ Please fill out all fields.")
        elif password != confirm_password:
            placeholder.error("⚠️ Passwords do not match. Please try again.")
        elif len(password) < 8:
            placeholder.error("⚠️ Password must be at least 8 characters long.")
        else:
            # 2. Prepare the data payload for the API
            user_data = {"email": email, "password": password}

            # 3. Send the request to the FastAPI endpoint
            try:
                response = requests.post(f"{API_URL}/auth/register", json=user_data)

                # 4. Handle the API response
                # SUCCESS: Corresponds to status_code=201
                if response.status_code == 201:
                    placeholder.success(
                        "✅ Registration successful! You can now log in."
                    )

                # FAILURE: Corresponds to HTTPException with status_code=400
                elif response.status_code == 400:
                    error_detail = response.json().get("detail")
                    placeholder.error(f"🚫 Registration failed: {error_detail}")

                # Handle other potential errors (like validation errors from Pydantic)
                elif response.status_code == 422:
                    placeholder.error(
                        "🚫 Invalid data provided. Please check your email format."
                    )

                else:
                    placeholder.error(
                        f"An server error occurred: Status {response.status_code}"
                    )

            except requests.exceptions.ConnectionError:
                placeholder.error(
                    "🔌 Could not connect to the API. Please ensure the backend is running."
                )
            except Exception as e:
                placeholder.error(f"An unexpected error occurred: {e}")

# If user IS logged in, show the main part of the app
else:
    st.sidebar.success("You are logged in.")
    st.sidebar.button("Logout", on_click=logout_user)
    st.sidebar.write(f"Your token: {jwt_token}")
    query_params = st.query_params

    if "id" not in query_params:
        portfolio_list_view()

        with st.form("create_portfolio_form", clear_on_submit=True):
            st.subheader("Create New Portfolio")
            portfolio_name = st.text_input("Portfolio Name")
            submitted = st.form_submit_button("Create Portfolio")
            if submitted:
                if not portfolio_name:
                    st.error("⚠️ Please enter a portfolio name.")
                else:
                    portfolio_data = {"name": portfolio_name}
                    try:
                        response = requests.post(
                            f"{API_URL}/portfolio/",
                            json=portfolio_data,
                            headers={"Authorization": f"Bearer {jwt_token}"},
                        )
                        if response.status_code == 201:
                            st.success("✅ Portfolio created successfully!")
                            st.rerun()
                        elif response.status_code == 409:
                            error_detail = response.json().get("detail")
                            st.error(f"🚫 Creation failed: {error_detail}")
                        else:
                            st.error(
                                f"An error occurred: Status {response.status_code}"
                            )
                    except requests.exceptions.ConnectionError:
                        st.error(
                            "🔌 Could not connect to the API. Please ensure the backend is running."
                        )
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")

        transaction_response = requests.get(
            f"{API_URL}/transaction/",
            headers={"Authorization": f"Bearer {jwt_token}"},
        )

        if transaction_response.status_code == 200:
            transactions = transaction_response.json()
            if transactions:
                df = pd.DataFrame(transactions)
                st.subheader("Your Transactions")
                st.dataframe(df)
            else:
                st.info("You have no transactions yet. Use the sidebar to create one.")
    else:
        portfolio_id = int(query_params["id"])
        portfolio_detail_view(portfolio_id)
