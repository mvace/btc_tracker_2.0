import streamlit as st
import auth
from components.forms import login_form


def login_view():
    st.write("Or, try the app with a demo account:")
    if st.button("🚀 Use Demo Account"):
        if auth.login_user("demoaccount@example.com", "demopass"):
            st.rerun()

    submitted, username, password = login_form()
    if submitted:
        auth.login_user(username, password)
