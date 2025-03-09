import datetime


def round_timestamp_to_nearest_hour(unix_timestamp: int) -> int:
    """
    Rounds a given Unix timestamp to the nearest hour.

    Args:
        unix_timestamp (int): The Unix timestamp (epoch) to round.

    Returns:
        int: The Unix timestamp rounded to the nearest hour. Timestamps with 29 minutes and 59 seconds or less round down, while 30 minutes or above rounds up to the next full hour.
    """
    SECONDS_IN_HOUR = 3600
    HALF_HOUR = 1800

    remainder = unix_timestamp % SECONDS_IN_HOUR
    if remainder < HALF_HOUR:
        return unix_timestamp - remainder
    else:
        return unix_timestamp + (SECONDS_IN_HOUR - remainder)


timestamps = [
    1732641540,
    1640483538,
    1641115923,
    1674038743,
    1692733399,
    1733220582,
    1736957497,
    1739010676,
    1631491355,
    1722381638,
]

for ts in timestamps:
    original_datetime = datetime.datetime.utcfromtimestamp(ts)
    rounded_ts = round_timestamp_to_nearest_hour(ts)
    rounded_datetime = datetime.datetime.utcfromtimestamp(rounded_ts)

    print(
        f"RoundedTS: {rounded_ts} -> Original: {original_datetime} -> Rounded: {rounded_datetime}"
    )
