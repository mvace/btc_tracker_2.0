# streamlit_app.py
import streamlit as st
import requests
import pandas as pd

from views.portfolio_details import portfolio_detail_view
from views.portfolio_list import portfolio_list_view
from views.transaction_list import transaction_list_view
from views.portfolio_create import portfolio_create_view
from views.login_view import login_view
from components.forms import create_portfolio_form

import api_client

import auth


# --- CONFIGURATION ---
st.set_page_config(
    page_title="Bitcoin Portfolio Tracker", page_icon="💰", layout="wide"
)
API_URL = "https://bitfolio.up.railway.app"
# --- AUTHENTICATION & STATE ---

# Initialize session state variables if they don't exist
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
# if "token" not in st.session_state:
#     st.session_state.token = ""

# --- UI ---

st.title("💰 Portfolio & Transaction Tracker")
jwt_token = auth.get_token()

# If user is not logged in, show login/register forms
if not jwt_token:
    st.subheader("Welcome! Please log in or register.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        login_view()
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
            st.error("⚠️ Please fill out all fields.")
        elif password != confirm_password:
            st.error("⚠️ Passwords do not match. Please try again.")
        elif len(password) < 8:
            st.error("⚠️ Password must be at least 8 characters long.")
        else:
            # 2. Prepare the data payload for the API
            user_data = {"email": email, "password": password}

            # 3. Send the request to the FastAPI endpoint
            try:
                status, data = auth.register_user(user_data)
                # 4. Handle the API response
                # SUCCESS: Corresponds to status_code=201
                if status == 201:
                    st.success("✅ Registration successful! You can now log in.")

                # FAILURE: Corresponds to HTTPException with status_code=400
                elif status == 400:
                    error_detail = data.get("detail")
                    st.error(f"🚫 Registration failed: {error_detail}")

                # Handle other potential errors (like validation errors from Pydantic)
                elif status == 422:
                    st.error(
                        "🚫 Invalid data provided. Please check your email format."
                    )

                else:
                    st.error(f"An server error occurred: Status {status}")

            except requests.exceptions.ConnectionError:
                st.error(
                    "🔌 Could not connect to the API. Please ensure the backend is running."
                )
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# If user IS logged in, show the main part of the app
else:
    st.sidebar.success("You are logged in.")
    st.sidebar.button("Logout", on_click=auth.logout_user)
    st.sidebar.write(f"Your token: {jwt_token}")
    query_params = st.query_params

    if "portfolio_id" not in query_params:
        portfolio_list_view(token=jwt_token)

        portfolio_data = create_portfolio_form()
        if portfolio_data:
            portfolio_create_view(token=jwt_token, payload=portfolio_data)

        transaction_list_view(token=jwt_token)

    else:
        portfolio_id = int(query_params["portfolio_id"])
        portfolio_detail_view(portfolio_id, jwt_token)
