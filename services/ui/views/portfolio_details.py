import streamlit as st
from datetime import datetime, timezone
from components.metrics import (
    show_goal_chart,
    show_portfolio_overview,
)
from components.forms import create_transaction_form
from views.transaction_list import transaction_list_view
import api_client
import auth


def portfolio_detail_view(portfolio_id: int, token: str):
    if st.button("← Back to all portfolios"):
        st.query_params.clear()
        st.rerun()

    status, data = api_client.get_portfolio_details(token, portfolio_id=portfolio_id)

    if status == 200:
        st.header(f"Portfolio: {data['name'].replace('_', ' ').title()}")

        overview_tab, transactions_tab = st.tabs(
            ["📊 Portfolio Overview", "📈 Transactions"]
        )

        with overview_tab:
            metrics_col, chart_col = st.columns([3, 2])
            with metrics_col:
                show_portfolio_overview(portfolio=data)

            with chart_col:
                show_goal_chart(portfolio=data)

        with transactions_tab:

            with st.popover("**➕ Add New Transaction**"):
                transaction_data = create_transaction_form(portfolio_id)
                if transaction_data:
                    create_status, create_data = api_client.create_transaction(
                        token, payload=transaction_data
                    )

                    if create_status == 201:
                        transaction_id = create_data.get("id", "N/A")
                        st.success(
                            f"✅ Transaction created successfully! ID: {transaction_id}"
                        )
                        st.rerun()
                    elif create_status in [400, 401, 403]:
                        error_message = create_data.get(
                            "detail", "An unknown client error occurred."
                        )
                        st.error(f"❌ Error: {error_message}")
                    elif create_status == 503:
                        st.error(f"🔌 Service Unavailable: {create_data.get('detail')}")
                    else:
                        st.error(
                            f"An unexpected server error occurred. Status code: {create_status}"
                        )

            st.header("Transaction History")
            transaction_list_view(token, portfolio_id)

    else:
        st.error("Portfolio not found.")
