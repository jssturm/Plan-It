"""Pydantic request models for API endpoints."""

import re
from typing import Optional

from pydantic import BaseModel, Field, model_validator

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
        "If omitted, the planner will flag it as unspecified rather than guessing.",
        examples=["Hyatt Regency Orlando, 9801 International Dr"],
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
        pattern=r"^(0?[1-9]|1[0-2]):[0-5]\d\s+(AM|PM)$",
        description="User-defined departure time in 12-hour format (e.g. '7:00 AM', '08:00 AM', '6:30 PM'). "
        "Hour must be 1-12, minute must be 00-59, and AM/PM suffix is required. "
        "If omitted, the departure time will be left blank in the itinerary.",
        examples=["7:00 AM", "08:00 AM", "6:30 PM"],
    )

    @model_validator(mode="after")
    def strip_and_validate(self) -> "TravelRequest":
        """Strip leading/trailing whitespace and reject obviously bogus input."""
        self.input = self.input.strip()
        if self.starting_location is not None:
            self.starting_location = self.starting_location.strip()
        if self.restaurant_preferences is not None:
            self.restaurant_preferences = self.restaurant_preferences.strip()
        if self.departure_time is not None:
            self.departure_time = self.departure_time.strip()
        if not self.input:
            raise ValueError("input must not be empty or whitespace-only")
        # Reject prompt-injection / system-override attempts before any
        # processing. This protects the planner from malicious input that
        # tries to override system instructions.  All user-supplied free-text
        # fields are checked, not just ``input``.
        if _contains_injection(self.input):
            raise ValueError("input contains disallowed content")
        if self.starting_location and _contains_injection(self.starting_location):
            raise ValueError("starting_location contains disallowed content")
        if self.restaurant_preferences and _contains_injection(self.restaurant_preferences):
            raise ValueError("restaurant_preferences contains disallowed content")
        return self
