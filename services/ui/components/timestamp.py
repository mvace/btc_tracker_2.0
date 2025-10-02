from datetime import datetime, timezone


def merged_timestamp(date, time):
    merged_datetime = datetime.combine(date, time)
    aware_datetime = merged_datetime.replace(tzinfo=timezone.utc)
    timestamp_str = aware_datetime.isoformat()
    if timestamp_str.endswith("+00:00"):
        timestamp_str = timestamp_str.replace("+00:00", "Z")
    return timestamp_str
