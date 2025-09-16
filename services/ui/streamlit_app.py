# streamlit_app.py
import streamlit as st
import requests
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Portfolio Tracker", page_icon="💰", layout="wide")

API_URL = "https://bitfolio.up.railway.app"
# --- AUTHENTICATION & STATE ---

# Initialize session state variables if they don't exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = ""


def login_user(username, password):
    """Function to log in a user and get a JWT token."""
    try:
        response = requests.post(
            f"{API_URL}/auth/token", data={"username": username, "password": password}
        )
        if response.status_code == 200:
            st.session_state.token = response.json().get("access_token")
            st.session_state.logged_in = True
            return True
        else:
            st.error(f"Login failed: {response.json().get('detail')}")
            return False
    except requests.exceptions.ConnectionError as e:
        st.error(
            f"Connection Error: Could not connect to the API. Is the backend running? Details: {e}"
        )
        return False


def logout_user():
    """Function to log out a user."""
    st.session_state.logged_in = False
    st.session_state.token = ""
    st.info("You have been logged out.")


# --- UI ---

st.title("💰 Portfolio & Transaction Tracker")

# If user is not logged in, show login/register forms
if not st.session_state.logged_in:
    st.subheader("Welcome! Please log in or register.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if login_user(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()  # Rerun to hide the form and show the main app
    placeholder = st.empty()
    with register_tab:
        with st.form("register_form", clear_on_submit=True):
            st.write("Please fill in the details below to register.")

            email = st.text_input("Email")
            password = st.text_input(
                "Password",
                type="password",
                help="Password must be at least 8 characters long.",
            )
            confirm_password = st.text_input("Confirm Password", type="password")

            # The submit button for the form
            submitted = st.form_submit_button("Register")

    # --- Form Submission Logic ---
    if submitted:
        # 1. Client-side validation for a better user experience
        if not email or not password or not confirm_password:
            placeholder.error("⚠️ Please fill out all fields.")
        elif password != confirm_password:
            placeholder.error("⚠️ Passwords do not match. Please try again.")
        elif len(password) < 8:
            placeholder.error("⚠️ Password must be at least 8 characters long.")
        else:
            # 2. Prepare the data payload for the API
            user_data = {"email": email, "password": password}

            # 3. Send the request to the FastAPI endpoint
            try:
                response = requests.post(f"{API_URL}/auth/register", json=user_data)

                # 4. Handle the API response
                # SUCCESS: Corresponds to status_code=201
                if response.status_code == 201:
                    placeholder.success(
                        "✅ Registration successful! You can now log in."
                    )

                # FAILURE: Corresponds to HTTPException with status_code=400
                elif response.status_code == 400:
                    error_detail = response.json().get("detail")
                    placeholder.error(f"🚫 Registration failed: {error_detail}")

                # Handle other potential errors (like validation errors from Pydantic)
                elif response.status_code == 422:
                    placeholder.error(
                        "🚫 Invalid data provided. Please check your email format."
                    )

                else:
                    placeholder.error(
                        f"An server error occurred: Status {response.status_code}"
                    )

            except requests.exceptions.ConnectionError:
                placeholder.error(
                    "🔌 Could not connect to the API. Please ensure the backend is running."
                )
            except Exception as e:
                placeholder.error(f"An unexpected error occurred: {e}")

# If user IS logged in, show the main part of the app
else:
    st.sidebar.success("You are logged in.")
    st.sidebar.button("Logout", on_click=logout_user)

    st.header("Homepage")
    st.write(
        "Welcome to your dashboard! Use the sidebar to navigate to your portfolio and transactions."
    )

    # You can add a summary or dashboard content here
    st.info("Select a page from the left to get started.")
