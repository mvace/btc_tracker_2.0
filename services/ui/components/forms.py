import streamlit as st
from decimal import Decimal
import plotly.graph_objects as go
from datetime import datetime, timezone
import requests
from components.timestamp import merged_timestamp


def transaction_create_form(portfolio_id):
    with st.form("create_transaction_form"):
        tranaction_amount = st.text_input(
            label="BTC Amount", placeholder="e.g., 0.12345678"
        )
        transaction_date = st.date_input(
            label="Date",
            min_value=datetime(2010, 7, 17, tzinfo=timezone.utc),
            max_value="today",
        )
        transaction_time = st.time_input("Time")
        submitted = st.form_submit_button("Add Transaction")
        tranaction_amount = tranaction_amount.replace(",", ".")
        try:
            tranaction_amount = Decimal(tranaction_amount)
            min_val = Decimal("0.00000001")
            max_val = Decimal("21000000")

            if not (min_val <= tranaction_amount <= max_val):
                st.error(f"Amount must be between {min_val} and {max_val}.")
        except:
            pass
        if submitted:
            timestamp = merged_timestamp(transaction_date, transaction_time)

            transaction_data = {
                "portfolio_id": portfolio_id,
                "btc_amount": str(tranaction_amount),
                "timestamp": timestamp,
            }
            return transaction_data
