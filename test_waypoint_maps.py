"""Tests for in-venue walking map destination helpers."""

from app.engine.planner import (
    _attraction_short_name,
    _map_destination,
    _venue_label,
    _walking_directions_url,
)


def test_venue_label_includes_location_when_distinct():
    assert _venue_label({"venue": "Busch Gardens", "location": "Tampa"}) == "Busch Gardens Tampa"
    assert _venue_label({"venue": "Busch Gardens Tampa", "location": "Tampa"}) == "Busch Gardens Tampa"


def test_map_destination_qualifies_attraction():
    assert _map_destination("Kumba", "Busch Gardens Tampa") == "Kumba, Busch Gardens Tampa"


def test_walking_directions_url_includes_venue_and_walking_mode():
    url = _walking_directions_url("Congo River Rapids", "Kumba", "Busch Gardens Tampa")
    assert "travelmode=walking" in url
    assert "origin=" in url and "destination=" in url
    assert "Busch" in url or "Busch%20" in url or "Busch+" in url


def test_attraction_short_name_strips_tip_suffix():
    assert _attraction_short_name("Kumba — tip: ride early") == "Kumba"
