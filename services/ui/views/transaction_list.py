import api_client
import streamlit as st
import pandas as pd
from components.metrics import show_transaction_list_metrics
import auth


def transaction_list_view(token):
    status, data = api_client.get_transaction_list(token)

    if status == 200:

        st.header(f"You have {len(data)} transactions.")
        if not data:
            st.info("You have no portfolios yet. Create one using the form below.")
        else:
            for portfolio in data:
                show_transaction_list_metrics(portfolio)

    elif status == 401:
        auth.logout_user()
        st.rerun()
    else:
        st.error("Failed to retrieve portfolios.")
