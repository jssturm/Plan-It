"""Tests for crowd prediction and live attraction waits."""

from datetime import date, timedelta
from unittest.mock import patch

from app.engine.crowd import (
    _crowd_from_avg_wait,
    _heuristic_crowd_level,
    _parse_attraction_label,
    _resolve_park_ids,
    estimate_attraction_wait,
    get_crowd_level_with_source,
)


def test_walt_disney_world_resolves_to_four_parks():
    assert _resolve_park_ids("Walt Disney World") == [6, 5, 7, 8]


def test_universal_orlando_includes_epic_and_volcano_bay():
    assert _resolve_park_ids("Universal Orlando") == [65, 64, 334, 67]


def test_disneyland_does_not_resolve_to_wdw():
    assert _resolve_park_ids("Disneyland") == [16]


def test_multi_park_aliases_covered():
    assert _resolve_park_ids("Busch Gardens Tampa") == [24]
    assert _resolve_park_ids("Cedar Point") == [50]
    assert _resolve_park_ids("Epic Universe") == [334]
    assert _resolve_park_ids("SeaWorld Orlando") == [21]
    assert _resolve_park_ids("Six Flags Magic Mountain") == [32]


def test_avg_wait_24_is_moderate_not_busy():
    assert _crowd_from_avg_wait(24.0) == 5


def test_heuristic_late_july_tuesday_disney_not_stuck_at_7():
    level = _heuristic_crowd_level("Walt Disney World", date(2026, 7, 28))
    assert 4 <= level <= 6


def test_live_source_when_waits_available():
    with patch("app.engine.crowd._fetch_open_wait_times", return_value=(20.0, 25.0, 30.0)):
        level, source = get_crowd_level_with_source("Magic Kingdom", date.today())
    assert source == "live"
    assert level == _crowd_from_avg_wait(25.0)


def test_future_date_uses_estimate_not_live():
    future = date.today() + timedelta(days=30)
    with patch("app.engine.crowd._live_crowd_level") as live:
        level, source = get_crowd_level_with_source("Magic Kingdom", future)
    live.assert_not_called()
    assert source == "estimate"
    assert 1 <= level <= 10


def test_parse_park_colon_ride_list():
    park, rides = _parse_attraction_label(
        "Magic Kingdom: Space Mountain, Seven Dwarfs Mine Train, Big Thunder Mountain"
    )
    assert park == "Magic Kingdom"
    assert rides == ["Space Mountain", "Seven Dwarfs Mine Train", "Big Thunder Mountain"]


def test_parse_ride_with_colon_in_name():
    park, rides = _parse_attraction_label("Guardians of the Galaxy: Cosmic Rewind")
    assert park == ""
    assert rides == ["Guardians of the Galaxy: Cosmic Rewind"]


def test_estimate_attraction_wait_matches_rides_across_parks():
    catalog_mk = (
        ("Space Mountain", 35.0),
        ("Seven Dwarfs Mine Train", 65.0),
        ("Big Thunder Mountain Railroad", 45.0),
    )
    catalog_epcot = (
        ("Guardians of the Galaxy: Cosmic Rewind", 75.0),
        ("Soarin' Across America", 40.0),
        ("Test Track", 50.0),
    )

    def fake_fetch(park_id):
        if park_id == 6:
            return catalog_mk
        if park_id == 5:
            return catalog_epcot
        return tuple()

    with patch("app.engine.crowd._fetch_park_ride_waits", side_effect=fake_fetch):
        mk = estimate_attraction_wait(
            "Magic Kingdom: Space Mountain, Seven Dwarfs Mine Train, Big Thunder Mountain",
            "Walt Disney World",
            target_date=date.today(),
        )
        epcot = estimate_attraction_wait(
            "EPCOT: Guardians of the Galaxy: Cosmic Rewind, Soarin', Test Track",
            "Walt Disney World",
            target_date=date.today(),
        )

    assert mk is not None
    assert mk["source"] == "live"
    assert mk["wait_min"] == 65  # max of matched
    assert "Seven Dwarfs Mine Train" in mk["matched"]

    assert epcot is not None
    assert epcot["wait_min"] == 75
    assert any("Guardians" in m for m in epcot["matched"])


def test_estimate_attraction_wait_busch_gardens_ride():
    with patch(
        "app.engine.crowd._fetch_park_ride_waits",
        return_value=(("Kumba", 5.0), ("Iron Gwazi", 30.0), ("SheiKra", 30.0)),
    ):
        result = estimate_attraction_wait("Kumba", "Busch Gardens Tampa", target_date=date.today())
    assert result is not None
    assert result["wait_min"] == 5
    assert result["matched"] == ["Kumba"]


def test_prefers_standard_queue_over_single_rider():
    catalog = (
        ("Star Wars: Rise of the Resistance Single Rider", 20.0),
        ("Star Wars: Rise of the Resistance", 45.0),
    )
    with patch("app.engine.crowd._fetch_park_ride_waits", return_value=catalog):
        result = estimate_attraction_wait(
            "Hollywood Studios: Rise of the Resistance",
            "Walt Disney World",
            target_date=date.today(),
        )
    assert result is not None
    assert result["matched"] == ["Star Wars: Rise of the Resistance"]
    assert result["wait_min"] == 45
