"""Unit tests for departure-time normalization."""

import pytest

from app.engine.planner import _normalize_departure_time


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("0800 AM", "08:00 AM"),
        ("0800AM", "08:00 AM"),
        ("0800", "08:00 AM"),
        ("0700", "07:00 AM"),
        ("800", "08:00 AM"),
        ("8:00 AM", "08:00 AM"),
        ("08:00", "08:00 AM"),
        ("7am", "07:00 AM"),
        ("7 AM", "07:00 AM"),
        ("7:00AM", "07:00 AM"),
        ("08", "08:00 AM"),
        ("8", "08:00 AM"),
        ("6:30 PM", "06:30 PM"),
        ("1830", "06:30 PM"),
        ("12:00 PM", "12:00 PM"),
        ("12:00 AM", "12:00 AM"),
        ("00:00", "12:00 AM"),
        ("  0800 am  ", "08:00 AM"),
    ],
)
def test_normalize_departure_time_extracts_valid_times(raw, expected):
    assert _normalize_departure_time(raw) == expected


def test_normalize_departure_time_unparseable_returns_raw():
    raw = "not-a-time"
    assert _normalize_departure_time(raw) == raw
