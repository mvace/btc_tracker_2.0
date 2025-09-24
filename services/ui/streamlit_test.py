import streamlit as st

# --- MOCK DATABASE ---
MOCK_TRANSACTIONS = {
    1: {"item": "Laptop", "amount": 1200, "customer": "Alice"},
    2: {"item": "Keyboard", "amount": 75, "customer": "Bob"},
    3: {"item": "Monitor", "amount": 300, "customer": "Alice"},
}


def get_all_transactions():
    return [{"id": id, **data} for id, data in MOCK_TRANSACTIONS.items()]


def get_transaction_by_id(transaction_id: int):
    return MOCK_TRANSACTIONS.get(transaction_id)


# --- END MOCK DATABASE ---


# --- VIEWS ---
def transaction_list_view():
    """Display the list of all transactions."""
    st.header("All Transactions")
    transactions = get_all_transactions()

    for tx in transactions:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.write(f"ID: {tx['id']}")
        with col2:
            st.write(f"Item: {tx['item']}")
        with col3:
            # CHANGE #1: Use st.button instead of st.link_button
            # A unique key is crucial for buttons inside a loop.
            if st.button("View Details", key=f"view_{tx['id']}"):
                # Set the query parameter to the transaction id
                st.query_params["id"] = tx["id"]
                st.rerun()  # Optional: Explicitly rerun for immediate effect
        st.divider()


def transaction_detail_view(transaction_id: int):
    """Display the details for a single transaction."""
    st.header(f"Transaction Details: ID {transaction_id}")

    # CHANGE #2: Use st.button for the back action
    if st.button("← Back to all transactions"):
        # Clear all query params to return to the list view
        st.query_params.clear()
        st.rerun()  # Optional: Explicitly rerun for immediate effect

    transaction = get_transaction_by_id(transaction_id)

    if transaction:
        st.subheader(f"Item: {transaction['item']}")
        st.write(f"**Amount:** ${transaction['amount']:,}")
        st.write(f"**Customer:** {transaction['customer']}")
    else:
        st.error("Transaction not found.")


# --- MAIN ROUTER LOGIC (No changes here) ---
st.set_page_config(layout="centered")
st.title("Transaction Dashboard")

query_params = st.query_params
st.write(f"{query_params}")

if "id" in query_params:
    st.write(f"{query_params}")
    transaction_id_to_show = int(query_params["id"])
    transaction_detail_view(transaction_id_to_show)
else:
    transaction_list_view()
