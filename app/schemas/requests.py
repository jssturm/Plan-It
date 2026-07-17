"""Pydantic request models for API endpoints."""

from typing import Optional

from pydantic import BaseModel, Field, model_validator


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
        return self
