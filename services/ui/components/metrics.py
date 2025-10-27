import streamlit as st
from decimal import Decimal, ROUND_HALF_UP
import plotly.graph_objects as go
from datetime import datetime
import api_client
from components.utils import format_usd
from components.timestamp import format_timestamp
from views.transaction_detail import transaction_details_dialog
import requests


def create_simple_donut_chart(portfolio):
    """
    Creates a Plotly donut chart with conditional coloring, optimized for a dark theme.

    Args:
        portfolio (dict): A dictionary containing 'current_value_usd' and 'goal_in_usd'.

    Returns:
        go.Figure: A Plotly figure object for the donut chart.
    """

    current = Decimal(portfolio["current_value_usd"])
    goal = Decimal(portfolio["goal_in_usd"])

    if goal > 0:
        progress_ratio = current / goal
    else:
        progress_ratio = Decimal(0)

    progress_percentage = int(
        (progress_ratio * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )

    if progress_percentage < 50:
        progress_color = "#3A86FF"
    elif 50 <= progress_percentage < 80:
        progress_color = "#4D96FF"
    elif 80 <= progress_percentage <= 100:
        progress_color = "#615fff"
    else:
        progress_color = "#28A745"

    remaining_color = "#314158"

    visual_progress = min(progress_ratio, Decimal(1))
    visual_remaining = Decimal(1) - visual_progress

    fig = go.Figure(
        go.Pie(
            values=[visual_progress, visual_remaining],
            hole=0.7,
            marker_colors=[
                progress_color,
                remaining_color,
            ],
            direction="clockwise",
            sort=False,
            showlegend=False,
            textinfo="none",
        )
    )

    fig.update_layout(
        annotations=[
            dict(
                text=f"<b>{progress_percentage}%</b>",
                x=0.5,
                y=0.5,
                font_size=28,
                showarrow=False,
                font=dict(color="#e2e8f0", family="Space Grotesk"),
            )
        ],
        height=250,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def show_goal_chart(portfolio: dict):
    with st.container(border=True):
        st.markdown(f"### 🎯 Goal Fulfillment")
        fig = create_simple_donut_chart(portfolio)
        st.plotly_chart(fig, use_container_width=True)


def show_portfolio_overview(portfolio: dict):
    with st.container(border=True):
        st.markdown("### 📈 Performance Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            label="💰 Current Value (USD)",
            value=f"${Decimal(portfolio['current_value_usd']):,.0f}",
            help="The total current market value of your holdings.",
        )

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

        st.divider()

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
    """A compact row using a colored badge for the ROI."""

    roi = float(portfolio.get("roi", 0))
    color = "green" if roi > 0 else "red"
    icon = "▲" if roi > 0 else "▼"
    roi_display = f"{icon} {roi:.2%}"

    with st.container(border=True):
        cols = st.columns([2, 4, 3, 2, 2, 1.5])

        cols[0].markdown(f"**{portfolio['name']}**")

        cols[1].markdown(
            f"**Current Value:** {format_usd(portfolio['current_value_usd'])}"
        )
        btc_amount = float(portfolio.get("total_btc_amount", 0))
        cols[2].markdown(f"**BTC:** {btc_amount:.8f} ₿")

        cols[3].markdown(
            f'<div style="background-color:{color}; color:white; padding:4px 10px; border-radius:15px; text-align:center; font-size:14px; font-weight:bold;">'
            f"{roi_display}"
            "</div>",
            unsafe_allow_html=True,
        )

        if cols[5].button(
            "View", key=f"view_potfolio_{portfolio['id']}", use_container_width=True
        ):
            st.query_params["portfolio_id"] = portfolio["id"]
            st.rerun()


def show_transaction_list_metrics(token, transaction):
    """A compact row using a colored badge for the ROI."""

    roi = float(transaction.get("roi", 0))
    color = "green" if roi > 0 else "red"
    icon = "▲" if roi > 0 else "▼"
    roi_display = f"{icon} {roi:.2%}"

    with st.container(border=True):
        cols = st.columns([2, 4, 3, 2, 2, 1.5])

        cols[0].markdown(f"{format_timestamp(transaction['timestamp_hour_rounded'])}")

        btc_amount = float(transaction.get("btc_amount", 0))

        cols[1].markdown(
            f"**Current Value:** {format_usd(transaction['current_value_usd'])}"
        )
        btc_amount = float(transaction.get("btc_amount", 0))
        cols[2].markdown(f"**BTC:** {btc_amount:.8f} ₿")

        cols[3].markdown(
            f'<div style="background-color:{color}; color:white; padding:4px 10px; border-radius:15px; text-align:center; font-size:14px; font-weight:bold;">'
            f"{roi_display}"
            "</div>",
            unsafe_allow_html=True,
        )

        if cols[5].button(
            "View",
            key=f"view_transaction_{transaction['id']}",
            use_container_width=True,
        ):
            transaction_details_dialog(token, transaction)


@st.cache_data(ttl=1800)
def get_bitcoin_price(api_key):
    """
    Fetches the current Bitcoin price and 24h change from CryptoCompare.
    """
    try:
        url = "https://min-api.cryptocompare.com/data/pricemultifull"
        params = {
            "fsyms": "BTC",
            "tsyms": "USD",
        }

        if api_key:
            params["api_key"] = api_key
        else:
            st.warning(
                "CryptoCompare API key is not set. You may hit rate limits.", icon="⚠️"
            )

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()["RAW"]["BTC"]["USD"]

        price = data["PRICE"]
        change_pct = data["CHANGEPCT24HOUR"]

        return price, change_pct

    except requests.RequestException as e:
        st.error(f"Error fetching BTC price from CryptoCompare: {e}")
        return None, None
    except (KeyError, TypeError, ValueError):
        st.error("Error parsing price data from CryptoCompare.")
        return None, None
