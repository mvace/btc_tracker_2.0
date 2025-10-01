import streamlit as st
from decimal import Decimal
import plotly.graph_objects as go


def show_goal_chart(portfolio: dict):

    fig = create_goal_chart(
        portfolio["current_value_usd"],
        portfolio["goal_in_usd"],
        portfolio["initial_value_usd"],
    )
    st.plotly_chart(fig, use_container_width=True)


def show_portfolio_overview(portfolio: dict):
    col1, col2, col3 = st.columns(3)

    col1.metric(
        label="USD invested",
        value=f"${Decimal(portfolio['initial_value_usd']):,.0f}",
    )

    col2.metric(
        label="Current Value (USD)",
        value=f"${Decimal(portfolio['current_value_usd']):,.0f}",
    )

    col3.metric(
        label="Net P&L (USD)",
        value=f"${Decimal(portfolio['net_result']):,.0f}",
        delta=f"{Decimal(portfolio['roi']):.2%}",
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        label="Average Price (USD)",
        value=f"${Decimal(portfolio['average_price_usd']):,.0f}",
    )

    col5.metric(
        label="ROI",
        value=f"{Decimal(portfolio['roi']):.2%}",
    )

    col6.metric(
        label="Total BTC Holdings",
        value=f"{Decimal(portfolio['total_btc_amount']):.8f} BTC",
    )


def get_gradient_color(progress_ratio):
    """
    Calculates a color in a red-yellow-green gradient based on a progress ratio (0.0 to 1.0).
    """
    # Clamp the ratio to be between 0 and 1
    progress_ratio = max(0, min(1, progress_ratio))

    # Define the start (red), middle (yellow), and end (green) colors in RGB
    start_rgb = (231, 76, 60)  # Red
    middle_rgb = (241, 196, 15)  # Yellow
    end_rgb = (46, 204, 113)  # Green

    if progress_ratio < 0.5:
        # Interpolate between red and yellow
        ratio = progress_ratio * 2
        r = int(start_rgb[0] + (middle_rgb[0] - start_rgb[0]) * ratio)
        g = int(start_rgb[1] + (middle_rgb[1] - start_rgb[1]) * ratio)
        b = int(start_rgb[2] + (middle_rgb[2] - start_rgb[2]) * ratio)
    else:
        # Interpolate between yellow and green
        ratio = (progress_ratio - 0.5) * 2
        r = int(middle_rgb[0] + (end_rgb[0] - middle_rgb[0]) * ratio)
        g = int(middle_rgb[1] + (end_rgb[1] - middle_rgb[1]) * ratio)
        b = int(middle_rgb[2] + (end_rgb[2] - middle_rgb[2]) * ratio)

    # Convert RGB to a hex string for Plotly
    return f"#{r:02x}{g:02x}{b:02x}"


def create_goal_chart(current_value_usd, goal_in_usd, initial_value_usd):
    """
    Creates an enhanced Plotly donut chart with a gradient color
    and detailed annotations.
    """
    # Convert inputs to Decimal for precision
    current = Decimal(current_value_usd)
    goal = Decimal(goal_in_usd)

    # --- 1. Calculations ---
    if goal > 0:
        progress_ratio = current / goal
        progress_percentage = round(progress_ratio * 100)
    else:
        progress_ratio = 0
        progress_percentage = 0

    # --- 2. Color Logic (NEW: Gradient based on progress) ---
    progress_color = get_gradient_color(float(progress_ratio))

    # --- 3. Chart Configuration ---
    visual_progress = min(current, goal)
    visual_remaining = max(0, goal - visual_progress)

    fig = go.Figure(
        go.Pie(
            values=[visual_progress, visual_remaining],
            hole=0.7,
            marker_colors=[progress_color, "#F2F3F4"],
            direction="clockwise",
            sort=False,
            showlegend=False,
            textinfo="none",
        )
    )

    # --- 4. Layout and Styling (NEW: Multi-line annotation) ---
    fig.update_layout(
        title_text="Goal Fulfillment",
        title_x=0.5,
        annotations=[
            dict(
                # Use HTML for multi-line text with different styles
                text=(
                    f"<b style='font-size: 1.4em;'>{progress_percentage}%</b><br>"
                    f"<span style='font-size: 0.8em; color: #555;'>"
                    f"${current:,.0f} / ${goal:,.0f}"
                    f"</span>"
                ),
                x=0.5,
                y=0.5,
                font_size=20,
                showarrow=False,
            )
        ],
        height=250,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig
