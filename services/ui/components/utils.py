from datetime import datetime


def format_timestamp(timestamp_str: str) -> str:
    """
    Parses an ISO format timestamp string and returns it in DD.MM.YYYY HH:MM format.
    Returns the original string if parsing fails or input is invalid.
    """
    if not timestamp_str:
        return "N/A"

    try:
        # Assuming timestamp is an ISO format string (e.g., '2023-10-27T14:00:00Z')
        # The .replace() handles the 'Z' for UTC timezone that fromisoformat can parse
        dt_object = datetime.fromisoformat(str(timestamp_str).replace("Z", "+00:00"))
        return dt_object.strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        # If parsing fails, show the original value as a fallback
        return str(timestamp_str)


def format_usd(value_str):
    """Safely converts a string to a float and formats as USD currency."""
    try:
        value = float(value_str)
        return f"${value:,.0f}"
    except (ValueError, TypeError):
        return "$0.00"
