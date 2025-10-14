import api_client
import streamlit as st
import pandas as pd
from components.metrics import show_transaction_list_metrics
import auth
from typing import Optional


def transaction_list_view(token: str, portfolio_id: Optional[int] = None):

    status, data = api_client.get_transaction_list(token, portfolio_id)

    if status == 200:

        st.header(f"You have {len(data)} transactions.")
        if not data:
            st.info("You have no portfolios yet. Create one using the form below.")
        else:
            for transaction in data:
                show_transaction_list_metrics(token, transaction)

    elif status == 401:
        auth.logout_user()
        st.rerun()
    else:
        st.error("Failed to retrieve transactions.")
