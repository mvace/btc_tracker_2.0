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


def round_timestamp_down_to_hour(unix_timestamp: int) -> int:
    """
    Rounds a given Unix timestamp down to the nearest full hour.

    Args:
        unix_timestamp (int): The Unix timestamp (epoch) to round.

    Returns:
        int: The Unix timestamp rounded down to the nearest full hour.
    """
    SECONDS_IN_HOUR = 3600
    return unix_timestamp - (unix_timestamp % SECONDS_IN_HOUR)
