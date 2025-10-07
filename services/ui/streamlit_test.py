import streamlit as st
import plotly.graph_objects as go
from decimal import Decimal, ROUND_HALF_UP


def create_simple_donut_chart(current_value, goal_value):
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
    current = Decimal(current_value)
    goal = Decimal(goal_value)

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
        progress_color = "#B0EBA1"  # Yellow
    elif 50 <= progress_percentage < 80:
        progress_color = "#ABEBC6"  # Light Green
    elif 80 <= progress_percentage <= 100:
        progress_color = "#2ECC71"  # Dark Green
    else:
        progress_color = "#8E44AD"  # Vibrant Purple for overachievement

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


# --- Streamlit App to Demonstrate the Chart ---
st.set_page_config(layout="centered")

st.title("Interactive Donut Chart")

st.write(
    "This chart simplifies the color logic and updates based on the slider value. "
    "For values over 100%, I've used a vibrant purple to indicate that the goal has been exceeded."
)

# Interactive slider for demonstration
goal = 1000
current = st.slider(
    "Current Value",
    min_value=0,
    max_value=1500,
    value=350,
    step=50,
    help=f"The goal is set to ${goal:,.0f}",
)

# Create and display the chart
st.markdown(f"### 🎯 Goal Fulfillment: `${current:,.0f}` / `${goal:,.0f}`")
fig = create_simple_donut_chart(current, goal)
st.plotly_chart(fig, use_container_width=True)

st.info(
    """
    **Color Logic:**
    - **Yellow:** < 50%
    - **Light Green:** 50% - 79%
    - **Dark Green:** 80% - 100%
    - **Purple:** > 100%
    """,
    icon="🎨",
)
