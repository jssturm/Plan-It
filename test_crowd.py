"""Tests for crowd prediction (heuristic + live mapping)."""

from datetime import date
from unittest.mock import patch

from app.engine.crowd import (
    _crowd_from_avg_wait,
    _heuristic_crowd_level,
    _resolve_park_ids,
    get_crowd_level_with_source,
)


def test_walt_disney_world_resolves_to_four_parks():
    assert _resolve_park_ids("Walt Disney World") == [6, 5, 7, 8]


def test_disneyland_does_not_resolve_to_wdw():
    assert _resolve_park_ids("Disneyland") == [16]


def test_avg_wait_24_is_moderate_not_busy():
    # Live WDW parks often sit ~20–25 min on a normal day — must not read as 7/10.
    assert _crowd_from_avg_wait(24.0) == 5


def test_heuristic_late_july_tuesday_disney_not_stuck_at_7():
    # Old multiplicative model always produced 7 for summer Disney weekdays.
    level = _heuristic_crowd_level("Walt Disney World", date(2026, 7, 28))
    assert 4 <= level <= 6


def test_live_source_when_waits_available():
    with patch("app.engine.crowd._fetch_open_wait_times", return_value=(20.0, 25.0, 30.0)):
        # Clear lru_cache on fetch if needed — patch replaces function
        level, source = get_crowd_level_with_source("Magic Kingdom", date.today())
    assert source == "live"
    assert level == _crowd_from_avg_wait(25.0)


def test_future_date_uses_estimate_not_live():
    from datetime import timedelta

    future = date.today() + timedelta(days=30)
    with patch("app.engine.crowd._live_crowd_level") as live:
        level, source = get_crowd_level_with_source("Magic Kingdom", future)
    live.assert_not_called()
    assert source == "estimate"
    assert 1 <= level <= 10
