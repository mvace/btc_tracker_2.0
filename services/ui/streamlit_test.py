import streamlit as st
import pandas as pd
import numpy as np

# Set the page title and a main header for the app
st.set_page_config(layout="wide")
st.title("Streamlit `@st.dialog` Decorator Demo")
st.write(
    "This app shows how to use `@st.dialog` as a decorator to create a modal window."
)


# --- Dialog Function ---
# The decorator turns this function into a dialog.
# The function's title becomes the dialog's title.
@st.dialog("Detailed Report")
def show_report_dialog():
    """This function contains all the content for the dialog."""
    st.header("Analysis of Widget Performance")
    st.write("This is a detailed view of the data, presented in a modal window.")

    # You can add any Streamlit element here, just like on the main page.
    st.subheader("Performance Chart")

    # Create a sample dataframe for the chart
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

    # Display a line chart inside the dialog
    st.line_chart(chart_data)

    st.subheader("Key Metrics")
    st.metric(label="Temperature", value="24 °C", delta="1.2 °C")
    st.metric(label="Active Users", value="1,245", delta="-3.4%")

    st.write("You can also include interactive widgets inside the dialog.")
    if st.button("Close Dialog"):
        # To close the dialog, you can simply rerun the app.
        # When the app reruns, the dialog function is no longer called,
        # so it disappears.
        st.rerun()


# --- Main Page Content ---
st.header("Main Page Content")
st.write(
    "This is the main area of the application. The content below will be overlaid by the dialog window."
)

# Create some columns for layout
col1, col2 = st.columns(2)

with col1:
    st.info("You can interact with elements on the main page here.")
    st.slider("A slider on the main page", 0, 100, 50)

with col2:
    st.warning("When the dialog is open, you cannot interact with the main page.")
    # When this button is clicked, the function with the @st.dialog decorator is called.
    if st.button("📊 Show Detailed Report"):
        show_report_dialog()

st.success("Click the 'Show Detailed Report' button above to see the dialog in action!")
