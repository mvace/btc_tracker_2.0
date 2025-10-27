import streamlit as st
from views.portfolio_details import portfolio_detail_view
from views.portfolio_list import portfolio_list_view
from views.transaction_list import transaction_list_view
from views.portfolio_create import portfolio_create_view
from views.login_view import login_view
from views.register_view import register_view
from components.forms import create_portfolio_form
from streamlit_cookies_manager import EncryptedCookieManager
from components.metrics import get_bitcoin_price
from components.css_components import font_css
import auth

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Bitcoin Portfolio Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(font_css, unsafe_allow_html=True)

API_URL = st.secrets["API_URL"]
CRYPTOCOMPARE_API_KEY = st.secrets["CRYPTOCOMPARE_API_KEY"]


# --- COOKIE SETUP ---
cookies = EncryptedCookieManager(password="my_secret_encryption_password")

if not cookies.ready():
    st.stop()

# Pass cookies to auth functions
auth.set_cookie_manager(cookies)


# --- UI ---

st.title("💰 Bitcoin Portfolio & Transaction Tracker")
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
    price, change = get_bitcoin_price(CRYPTOCOMPARE_API_KEY)
    if price is not None and change is not None:
        st.sidebar.metric(
            label="Bitcoin (BTC) Price",
            value=f"${price:,.2f}",
            delta=f"{change:.2f}% (24h)",
        )

    st.sidebar.success("You are logged in.")
    st.sidebar.button("Logout", on_click=auth.logout_user)

    query_params = st.query_params

    if "portfolio_id" not in query_params:

        tab_portfolios, tab_transactions = st.tabs(
            ["My Portfolios", "All Transactions"]
        )

        with tab_portfolios:
            st.header("Your Portfolios")

            # --- NEW: Put the create form in an expander ---
            with st.popover("➕ Create New Portfolio"):
                portfolio_data = create_portfolio_form()
                if portfolio_data:
                    portfolio_create_view(token=jwt_token, payload=portfolio_data)

            # Show the list *after* the (collapsed) form
            portfolio_list_view(token=jwt_token)

        with tab_transactions:
            st.subheader("All Recent Transactions")
            transaction_list_view(token=jwt_token)

    else:
        # This part for viewing details remains the same
        portfolio_id = int(query_params["portfolio_id"])
        portfolio_detail_view(portfolio_id, jwt_token)
