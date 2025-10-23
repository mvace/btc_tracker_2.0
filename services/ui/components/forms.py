import streamlit as st
from decimal import Decimal
import plotly.graph_objects as go
from datetime import datetime, timezone, date, timedelta
from components.timestamp import merged_timestamp


def create_transaction_form(portfolio_id):
    today = date.today()
    yesterday_date = today - timedelta(days=1)
    with st.form("create_transaction_form"):
        tranaction_amount = st.text_input(
            label="BTC Amount", placeholder="e.g., 0.12345678"
        )
        transaction_date = st.date_input(
            value=yesterday_date,
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


def create_portfolio_form():
    with st.form("create_portfolio_form", clear_on_submit=True):
        st.subheader("Create New Portfolio")
        portfolio_name = st.text_input("Portfolio Name")
        portfolio_goal = st.text_input("Your investment goal in USD")
        submitted = st.form_submit_button("Create Portfolio")
        if submitted:
            if not portfolio_name or not portfolio_goal:
                st.error("⚠️ Please fill the form correctly")
            else:
                portfolio_data = {
                    "name": portfolio_name,
                    "goal_in_usd": portfolio_goal,
                }
                return portfolio_data


def login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        return submitted, username, password


def register_form():
    with st.form("register_form", clear_on_submit=True):
        st.write("Please fill in the details below to register.")

        email = st.text_input("Email")
        password = st.text_input(
            "Password",
            type="password",
            help="Password must be at least 8 characters long.",
        )
        confirm_password = st.text_input("Confirm Password", type="password")

        submitted = st.form_submit_button("Register")

        if submitted:
            if not email or not password or not confirm_password:
                st.error("⚠️ Please fill out all fields.")
            elif password != confirm_password:
                st.error("⚠️ Passwords do not match. Please try again.")
            elif len(password) < 8:
                st.error("⚠️ Password must be at least 8 characters long.")
            else:
                user_data = {"email": email, "password": password}
                return submitted, user_data
    return False, None
