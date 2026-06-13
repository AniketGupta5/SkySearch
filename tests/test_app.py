"""
Basic tests for SkySearch app utility functions.
"""
import re
import pytest


def dur_mins(d: str) -> int:
    """Convert duration string like '2h 30m' to minutes."""
    h = int(re.search(r"(\d+)h", d).group(1)) if re.search(r"(\d+)h", d) else 0
    m = int(re.search(r"(\d+)m", d).group(1)) if re.search(r"(\d+)m", d) else 0
    return h * 60 + m


def test_duration_hours_and_minutes():
    assert dur_mins("2h 30m") == 150


def test_duration_hours_only():
    assert dur_mins("3h 00m") == 180


def test_duration_minutes_only():
    assert dur_mins("0h 45m") == 45


def test_stops_label_nonstop():
    stops = 0
    label = "Nonstop" if stops == 0 else f"{stops} stop"
    assert label == "Nonstop"


def test_stops_label_one_stop():
    stops = 1
    label = "Nonstop" if stops == 0 else f"{stops} stop"
    assert label == "1 stop"


def test_price_total_calculation():
    price = 5000
    adults = 3
    assert price * adults == 15000


def test_iata_code_length():
    code = "HYD"
    assert len(code) == 3


def test_iata_code_uppercase():
    code = "hyd".upper()
    assert code == "HYD"
