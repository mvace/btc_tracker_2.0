from datetime import datetime, timezone
from zoneinfo import ZoneInfo

LOCAL_TIMEZONE = ZoneInfo("Europe/Prague")


def merged_timestamp(date, time) -> str:
    """
    Combines a naive date and time, assumes it's in the local Prague
    timezone, and converts it to a UTC ISO string.
    """

    naive_datetime = datetime.combine(date, time)
    local_aware_datetime = naive_datetime.replace(tzinfo=LOCAL_TIMEZONE)
    utc_aware_datetime = local_aware_datetime.astimezone(timezone.utc)
    timestamp_str = utc_aware_datetime.isoformat()

    if timestamp_str.endswith("+00:00"):
        timestamp_str = timestamp_str.replace("+00:00", "Z")

    return timestamp_str


def format_timestamp(utc_timestamp_str: str) -> str:
    """
    Converts a UTC ISO timestamp string to a formatted, user-friendly
    string in the local Prague timezone.
    """
    if not utc_timestamp_str:
        return "N/A"

    if utc_timestamp_str.endswith("Z"):
        utc_timestamp_str = utc_timestamp_str.replace("Z", "+00:00")

    try:
        utc_dt = datetime.fromisoformat(utc_timestamp_str)
        local_dt = utc_dt.astimezone(LOCAL_TIMEZONE)
        return local_dt.strftime("%d.%m.%Y %H:%M")

    except (ValueError, TypeError):
        return "Invalid Date"
