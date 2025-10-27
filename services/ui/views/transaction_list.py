import api_client
import streamlit as st
import pandas as pd
from components.metrics import show_transaction_list_metrics
import auth
from typing import Optional


def transaction_list_view(token: str, portfolio_id: Optional[int] = None):

    status, data = api_client.get_transaction_list(token, portfolio_id)

    if status == 200:

        st.subheader(f"You have {len(data)} transactions")
        if not data:
            st.info("You have no portfolios yet. Create one using the form above.")
        else:
            for transaction in data:
                show_transaction_list_metrics(token, transaction)
    elif status == 404:
        st.info("You have no transactions yet.")
    else:
        st.error("Failed to retrieve transactions.")
