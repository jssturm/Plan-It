"""Pydantic request models for API endpoints."""

import re
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.engine.addressparse import normalize_us_address
from app.engine.timeparse import normalize_time

# Patterns that indicate prompt injection or system-instruction override attempts.
# These are rejected at the API boundary before any processing occurs.
_PROMPT_INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"\[system\]", re.IGNORECASE),
    re.compile(r"ignore\s+all\s+(previous\s+)?instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+(now|a\s+different)\s+(an?\s+)?\w+", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous\s+)?instructions", re.IGNORECASE),
    re.compile(r"override\s+(all\s+)?(system\s+)?(prompts?|instructions?)", re.IGNORECASE),
    re.compile(r"<\|.*\|>", re.IGNORECASE),  # LLM special token delimiters
]


def _contains_injection(text: str) -> bool:
    """Return True if *text* matches any known prompt-injection pattern."""
    return any(pat.search(text) for pat in _PROMPT_INJECTION_PATTERNS)


class TravelRequest(BaseModel):
    """Validated request body for /travel and /start-day endpoints."""

    input: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural-language travel plan description",
        examples=["Plan my trip to Kennedy Space Center tomorrow with lunch stop"],
    )
    starting_location: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Where the trip starts from (e.g. home address, hotel name). "
        "Free-form US addresses are accepted (commas optional) and normalized when possible.",
        examples=[
            "Hyatt Regency Orlando, 9801 International Dr",
            "9801 International Dr Orlando FL 32819",
        ],
    )
    restaurant_preferences: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=1000,
        description="Dietary restrictions, cuisine preferences, or specific restaurant "
        "requests for meal stops (e.g. 'vegetarian, prefer Italian, no fast food')",
        examples=["vegetarian, prefer Italian, $$-$$$ range"],
    )
    default_reminder_min: Optional[int] = Field(
        default=None,
        ge=5,
        le=60,
        description="Default reminder minutes to apply to every schedule item. "
        "Users can override individual items after generation.",
    )
    departure_time: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=30,
        description="User-defined departure time. Accepts free-form values such as "
        "'7:00 AM', '07:00', '7am', '0700', or '0800 AM' and normalizes to "
        "'HH:MM AM/PM'. If omitted, the departure time is left blank.",
        examples=["7:00 AM", "08:00 AM", "0800 AM", "6:30 PM"],
    )

    @model_validator(mode="after")
    def strip_and_validate(self) -> "TravelRequest":
        """Strip, normalize free-form fields, and reject injection attempts."""
        self.input = self.input.strip()
        if self.starting_location is not None:
            self.starting_location = normalize_us_address(self.starting_location.strip())
        if self.restaurant_preferences is not None:
            self.restaurant_preferences = self.restaurant_preferences.strip()
        if self.departure_time is not None:
            normalized = normalize_time(self.departure_time.strip())
            if not re.match(r"^\d{1,2}:\d{2}\s*(AM|PM)", normalized, re.IGNORECASE):
                raise ValueError(
                    "departure_time could not be parsed — try formats like "
                    "'7:00 AM', '0700', or '8am'"
                )
            self.departure_time = normalized
        if not self.input:
            raise ValueError("input must not be empty or whitespace-only")
        if _contains_injection(self.input):
            raise ValueError("input contains disallowed content")
        if self.starting_location and _contains_injection(self.starting_location):
            raise ValueError("starting_location contains disallowed content")
        if self.restaurant_preferences and _contains_injection(self.restaurant_preferences):
            raise ValueError("restaurant_preferences contains disallowed content")
        return self
