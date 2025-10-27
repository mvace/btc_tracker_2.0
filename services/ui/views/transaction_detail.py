import streamlit as st
import api_client
from components.utils import format_usd
from components.timestamp import format_timestamp


@st.dialog("Transaction Details")
def transaction_details_dialog(token, transaction):
    st.caption(f"Date: {format_timestamp(transaction.get('timestamp_hour_rounded'))}")
    st.divider()

    net_result = float(transaction.get("net_result", 0))
    roi = float(transaction.get("roi", 0))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h6>Purchase</h6>", unsafe_allow_html=True)
        st.metric("Invested", format_usd(transaction.get("initial_value_usd", 0)))
        st.metric(
            "BTC Price at purchase", format_usd(transaction.get("price_at_purchase", 0))
        )
        st.metric("BTC Amount", f"{float(transaction.get('btc_amount', 0)):.8f} ₿")

    with col2:
        st.markdown("<h6>Performance</h6>", unsafe_allow_html=True)
        st.metric("Current Value", format_usd(transaction.get("current_value_usd", 0)))
        st.metric("Net Result", format_usd(net_result), delta=f"{roi:.2%}")

    b_col1, b_col2 = st.columns(2)

    with b_col1:
        if st.button(
            "Delete Transaction",
            key=f"delete_{transaction['id']}",
            use_container_width=True,
            type="primary",
        ):
            status_code, data = api_client.delete_transaction(token, transaction["id"])

            if status_code == 204:
                st.toast(
                    f"Transaction {transaction['id']} deleted successfully.", icon="✅"
                )
                st.rerun()
            else:
                error_message = data.get("detail", "An unknown error occurred.")
                st.error(f"Error: {error_message}")

    with b_col2:
        if st.button(
            "Close", key=f"close_dialog_{transaction['id']}", use_container_width=True
        ):
            st.rerun()
