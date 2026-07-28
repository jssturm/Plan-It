"""Unit tests for free-form US address normalization."""

import pytest

from app.engine.addressparse import normalize_us_address, parse_us_address


@pytest.mark.parametrize(
    "raw,expected_street,expected_city,expected_state,expected_zip",
    [
        (
            "9801 International Dr, Orlando, FL 32819",
            "9801 International Dr",
            "Orlando",
            "FL",
            "32819",
        ),
        (
            "9801 International Dr Orlando FL 32819",
            "9801 International Dr",
            "Orlando",
            "FL",
            "32819",
        ),
        (
            "9801 International Drive Orlando Florida 32819",
            "9801 International Drive",
            "Orlando",
            "FL",
            "32819",
        ),
        (
            "Orlando, FL",
            "",
            "Orlando",
            "FL",
            "",
        ),
        (
            "Orlando FL 32819",
            "",
            "Orlando",
            "FL",
            "32819",
        ),
    ],
)
def test_parse_us_address_parts(raw, expected_street, expected_city, expected_state, expected_zip):
    parts = parse_us_address(raw)
    assert parts["street"] == expected_street
    assert parts["city"] == expected_city
    assert parts["state"] == expected_state
    assert parts["zip"] == expected_zip


def test_normalize_inserts_commas_for_run_on_address():
    assert normalize_us_address("9801 International Dr Orlando FL 32819") == (
        "9801 International Dr, Orlando FL 32819"
    )


def test_normalize_preserves_landmark_without_state():
    raw = "Hyatt Regency Orlando"
    assert normalize_us_address(raw) == raw


def test_travel_request_accepts_freeform_time_and_address():
    from app.schemas.requests import TravelRequest

    req = TravelRequest(
        input="Trip to Disney",
        starting_location="9801 International Dr Orlando FL 32819",
        departure_time="0800 AM",
    )
    assert req.departure_time == "08:00 AM"
    assert "Orlando" in req.starting_location
    assert "FL" in req.starting_location
