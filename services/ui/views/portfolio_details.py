import streamlit as st
from datetime import datetime, timezone



def portfolio_detail_view(portfolio_id: int, token: str):
    if st.button("← Back to all portfolios"):
        # Clear all query params to return to the list view
        st.query_params.clear()
        st.rerun()  # Optional: Explicitly rerun for immediate effect

    portfolio_response = requests.get(
        f"{API_URL}/portfolio/{portfolio_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    if portfolio_response.status_code == 200:
        portfolio = portfolio_response.json()

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
                    "portfolio_id": portfolio_id,
                    "btc_amount": str(tranaction_amount),
                    "timestamp": timestamp_str,
                }
                try:
                    response = requests.post(
                        f"{API_URL}/transaction/",
                        json=transaction_data,
                        headers={"Authorization": f"Bearer {jwt_token}"},
                    )
                    if response.status_code == 201:
                        st.success("✅ Transaction created successfully!")
                        st.rerun()

                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

    elif portfolio_response.status_code == 401:
        logout_user()
        st.rerun()

    else:
        st.error("Portfolio not found.")
