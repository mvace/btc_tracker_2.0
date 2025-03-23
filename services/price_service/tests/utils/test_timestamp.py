from app.utils.timestamp import (
    round_timestamp_to_nearest_hour,
    round_timestamp_down_to_hour,
)


def test_round_timestamp_to_nearest_hour_down():
    # Tuesday 14. November 2023 22:20:00
    ts = 1700000400
    assert (
        round_timestamp_to_nearest_hour(ts) == 1699999200
    )  # Tuesday 14. November 2023 22:00:00


def test_round_timestamp_to_nearest_hour_up():
    # Sunday 23. March 2025 15:30:00
    ts = 1742743800
    assert (
        round_timestamp_to_nearest_hour(ts) == 1742745600
    )  # Sunday 23. March 2025 16:00:00


def test_round_timestamp_to_nearest_hour_exact_hour():
    # Sunday 23. March 2025 16:00:00
    ts = 1742745600
    assert (
        round_timestamp_to_nearest_hour(ts) == 1742745600
    )  # Sunday 23. March 2025 16:00:00


def test_round_timestamp_down_to_hour_exact():
    # Sunday 23. March 2025 15:46:37
    ts = 1742744797
    assert (
        round_timestamp_down_to_hour(ts) == 1742742000
    )  # Sunday 23. March 2025 15:00:00


def test_round_timestamp_down_to_hour_inbetween():
    # Sunday 23. March 2025 15:59:59
    ts = 1742745599
    assert (
        round_timestamp_down_to_hour(ts) == 1742742000
    )  # Sunday 23. March 2025 15:00:00
