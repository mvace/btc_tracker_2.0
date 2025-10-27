from datetime import datetime


def format_usd(value_str):
    """Safely converts a string to a float and formats as USD currency."""
    try:
        value = float(value_str)
        return f"${value:,.0f}"
    except (ValueError, TypeError):
        return "$0.00"
