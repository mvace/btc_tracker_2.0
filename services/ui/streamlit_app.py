# streamlit_app.py
import streamlit as st

from views.portfolio_details import portfolio_detail_view
from views.portfolio_list import portfolio_list_view
from views.transaction_list import transaction_list_view
from views.portfolio_create import portfolio_create_view
from views.login_view import login_view
from views.register_view import register_view
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
        register_view()

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
