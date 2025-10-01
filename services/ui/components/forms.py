import streamlit as st
from decimal import Decimal
import plotly.graph_objects as go
from datetime import datetime, timezone
import requests
from metrics import 


def transaction_create_form(portfolio: dict, api_url: str, token: str):
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

            merged_datetime = datetime.combine(transaction_date, transaction_time)
            aware_datetime = merged_datetime.replace(tzinfo=timezone.utc)
            timestamp_str = aware_datetime.isoformat()
            if timestamp_str.endswith("+00:00"):
                timestamp_str = timestamp_str.replace("+00:00", "Z")
            transaction_data = {
                "portfolio_id": portfolio.id,
                "btc_amount": str(tranaction_amount),
                "timestamp": timestamp_str,
            }
            try:
                response = requests.post(
                    f"{api_url}/transaction/",
                    json=transaction_data,
                    headers={"Authorization": f"Bearer {token}"},
                )
                if response.status_code == 201:
                    st.success("✅ Transaction created successfully!")
                    st.rerun()

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

