import streamlit as st
import auth
from components.forms import register_form


def register_view():
    submitted, user_data = register_form()
    if submitted:
        # 3. Send the request to the FastAPI endpoint
        try:
            status, data = auth.register_user(user_data)
            # 4. Handle the API response
            # SUCCESS: Corresponds to status_code=201
            if status == 201:
                st.success("✅ Registration successful! You can now log in.")

            # FAILURE: Corresponds to HTTPException with status_code=400
            elif status == 400:
                error_detail = data.get("detail")
                st.error(f"🚫 Registration failed: {error_detail}")

            # Handle other potential errors (like validation errors from Pydantic)
            elif status == 422:
                st.error("🚫 Invalid data provided. Please check your email format.")

            else:
                st.error(f"An server error occurred: Status {status}")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
