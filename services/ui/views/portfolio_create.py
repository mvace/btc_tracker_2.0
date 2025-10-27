import streamlit as st
import api_client


def portfolio_create_view(token, payload):
    status, data = api_client.create_portfolio(token, payload)
    if status == 201:
        st.success(f"✅ Portfolio created successfully!")
        st.rerun()
    elif status in [400, 401, 403, 422]:
        error_message = data.get("detail", "An unknown client error occurred.")
        st.error(f"❌ Error: {error_message}")
    elif status == 503:
        st.error(f"🔌 Service Unavailable: {data.get('detail')}")
    else:
        st.error(f"An unexpected server error occurred. Status code: {status}")
