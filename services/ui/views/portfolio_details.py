import streamlit as st
from datetime import datetime, timezone
from components.metrics import show_goal_chart, show_portfolio_overview
from components.forms import transaction_create_form
import api_client
import auth


def portfolio_detail_view(portfolio_id: int, token: str):
    if st.button("← Back to all portfolios"):
        # Clear all query params to return to the list view
        st.query_params.clear()
        st.rerun()  # Optional: Explicitly rerun for immediate effect

    portfolio, status = api_client.get_portfolio_details(
        token, portfolio_id=portfolio_id
    )

    if status == 200:
        st.header(f"Portfolio Overview: {portfolio['name'].replace('_', ' ').title()}")
        chart_col, metrics_col = st.columns(
            [2, 3]
        )  # Allocate space for chart and metrics

        with chart_col:
            # Generate and display the chart
            show_goal_chart(portfolio=portfolio)

        with metrics_col:
            show_portfolio_overview(portfolio=portfolio)

        st.header(f"Add new Transaction")

        transaction_data = transaction_create_form(portfolio_id)
        status, data = api_client.post_transaction(token, payload=transaction_data)
        if transaction_data:
            if status == 201:
                # You might get the created transaction back in `data`
                transaction_id = data.get("id", "N/A")
                st.success(f"✅ Transaction created successfully! ID: {transaction_id}")
            elif status in [400, 401, 403]:
                # Extract the detailed error message from the API response
                error_message = data.get("detail", "An unknown client error occurred.")
                st.error(f"❌ Error: {error_message}")
            elif status == 503:
                st.error(f"🔌 Service Unavailable: {data.get('detail')}")
            else:
                # A catch-all for other server-side errors
                st.error(f"An unexpected server error occurred. Status code: {status}")

    elif status == 401:
        auth.logout_user()
        st.rerun()

    else:
        st.error("Portfolio not found.")
