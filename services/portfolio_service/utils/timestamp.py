from datetime import datetime, timezone, timedelta

# This is a true constant, so it's fine here.
FIRST_HISTORICAL_TIMESTAMP = datetime(2010, 7, 17, 0, 30, 0, tzinfo=timezone.utc)


def get_last_valid_timestamp() -> datetime:
    """
    Returns the last valid transaction timestamp, which is the 29th minute and
    59th second of the previous hour in UTC.
    """
    return (datetime.now(timezone.utc) - timedelta(hours=1)).replace(
        minute=29, second=59, microsecond=0
    )
