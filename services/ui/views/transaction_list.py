import api_client
import streamlit as st
import pandas as pd


def transaction_list_view(token):
    status, data = api_client.get_transaction_list(token)

    if status == 200:
        if data:
            df = pd.DataFrame(data)
            st.subheader("Your Transactions")
            st.dataframe(df)
        else:
            st.info("You have no transactions yet. Use the sidebar to create one.")
    else:
        st.error(f"An unexpected server error occurred. Status code: {status}")
