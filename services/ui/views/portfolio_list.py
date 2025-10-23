import streamlit as st
import auth
import api_client
from components.metrics import show_portfolio_list_metrics


def portfolio_list_view(token: str):
    """Display the list of all portfolios."""

    status, data = api_client.get_portfolio_list(token)

    if status == 200:

        st.subheader(f"You have {len(data)} portfolios.")
        if not data:
            st.info("You have no portfolios yet. Create one using the form below.")
        else:
            for portfolio in data:
                show_portfolio_list_metrics(portfolio)

    elif status == 401:
        auth.logout_user()
        st.rerun()
    else:
        st.error("Failed to retrieve portfolios.")
