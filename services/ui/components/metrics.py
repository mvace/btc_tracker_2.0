import streamlit as st
from decimal import Decimal, ROUND_HALF_UP
import plotly.graph_objects as go


def create_simple_donut_chart(portfolio):
    """
    Creates a simple Plotly donut chart with conditional coloring.

    - Yellow: < 50%
    - Light Green: 50% - 80%
    - Dark Green: 80% - 100%
    - Purple (Vibrant): > 100%

    Args:
        current_value (float or int): The current progress value.
        goal_value (float or int): The target goal value.

    Returns:
        go.Figure: A Plotly figure object for the donut chart.
    """

    current = Decimal(portfolio["current_value_usd"])
    goal = Decimal(portfolio["goal_in_usd"])

    # 1. Calculate Progress and Handle Division by Zero
    if goal > 0:
        progress_ratio = current / goal
    else:
        progress_ratio = Decimal(0)

    # Use ROUND_HALF_UP for standard rounding
    progress_percentage = int(
        (progress_ratio * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )

    # 2. Determine Color Based on Progress
    if progress_percentage < 50:
        progress_color = "#B0EBA1"  # Light Pastel Green
    elif 50 <= progress_percentage < 80:
        progress_color = "#82E0AA"  # Medium-light Green
    elif 80 <= progress_percentage <= 100:
        progress_color = "#2ECC71"  # Standard Green
    else:
        progress_color = "#1E8449"  # Dark, Rich Green for overachievement
    # 3. Define Chart Values
    # The visible portion of the donut should not exceed 100%
    visual_progress = min(progress_ratio, Decimal(1))
    visual_remaining = Decimal(1) - visual_progress

    # 4. Create the Figure
    fig = go.Figure(
        go.Pie(
            values=[visual_progress, visual_remaining],
            hole=0.7,
            marker_colors=[
                progress_color,
                "#EAECEE",
            ],  # Color for progress and for the remaining part
            direction="clockwise",
            sort=False,
            showlegend=False,
            textinfo="none",  # We will add custom text in the layout
        )
    )

    # 5. Update Layout for Styling and Center Text
    fig.update_layout(
        # Add the percentage text in the center
        annotations=[
            dict(
                text=f"<b>{progress_percentage}%</b>",
                x=0.5,
                y=0.5,
                font_size=28,
                showarrow=False,
                font=dict(color="#333", family="sans-serif"),
            )
        ],
        height=250,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def show_goal_chart(portfolio: dict):
    # NEW: Wrap the chart in a container to match the metrics card
    with st.container(border=True):
        st.markdown(f"### 🎯 Goal Fulfillment")
        fig = create_simple_donut_chart(portfolio)
        st.plotly_chart(fig, use_container_width=True)
        # st.markdown(
        # f"## `${Decimal(portfolio['current_value_usd']):,.0f}` / `${Decimal(portfolio['goal_in_usd']):,.0f}`",
        # width="stretch",


def show_portfolio_overview(portfolio: dict):
    with st.container(border=True):
        st.markdown("### 📈 Performance Overview")

        # --- First Row: Top-line results (Value and Profit) ---
        col1, col2, col3 = st.columns(3)

        col1.metric(
            label="💰 Current Value (USD)",
            value=f"${Decimal(portfolio['current_value_usd']):,.0f}",
            help="The total current market value of your holdings.",
        )

        # The delta automatically shows green for profit and red for loss
        col2.metric(
            label="💸 Net P&L (USD)",
            value=f"${Decimal(portfolio['net_result']):,.0f}",
            delta=f"{Decimal(portfolio['roi']):.2%}",
            help="Net Profit & Loss and the corresponding Return on Investment (ROI).",
        )

        col3.metric(
            label="🎯 Goal (USD)",
            value=f"${Decimal(portfolio['goal_in_usd']):,.0f}",
            help="Your portfolio target value.",
        )

        st.divider()  # Visual separator for clarity

        # --- Second Row: Investment details ---
        col4, col5, col6 = st.columns(3)

        col4.metric(
            label="💵 Initial Investment",
            value=f"${Decimal(portfolio['initial_value_usd']):,.0f}",
        )

        col5.metric(
            label="⚖️ Average Price",
            value=f"${Decimal(portfolio['average_price_usd']):,.2f}",
        )

        col6.metric(
            label="₿ Total BTC Holdings",
            value=f"{Decimal(portfolio['total_btc_amount']):.8f}",
        )


def show_portfolio_list_metrics(portfolio):
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])  # Give more space to info, less to the button

        with col1:
            # Use markdown for a larger, bolded name
            st.markdown(f"#### {portfolio['name']}")
            # Use a caption or simple markdown for the secondary information (the goal)
            st.caption(f"Investment Goal: {portfolio['goal_in_usd']}")

        with col2:
            # The button to view details. Using a simple arrow can look cleaner.
            # We add a bit of vertical space to help align it, though perfect
            # vertical alignment in Streamlit can be tricky without CSS.
            st.write("")  # A little vertical space
            if st.button(
                "View ➔", key=f"view_{portfolio['id']}", use_container_width=True
            ):
                st.query_params["portfolio_id"] = portfolio["id"]
                st.rerun()
