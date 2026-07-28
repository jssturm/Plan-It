"""Pydantic models for validated travel itinerary data."""

import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

# Driving directions: single-destination format (no origin param)
_URL_PATTERN = re.compile(r"^https://(www\.)?google\.com/maps/dir/\?api=1&.*destination=")

# Walking directions: origin + destination + walking mode — used for intra-venue maps
_WALK_URL_PATTERN = re.compile(
    r"^https://(www\.)?google\.com/maps/dir/\?api=1&.*origin=.*&.*destination=.*&travelmode=walking"
)


class Stop(BaseModel):
    """A single route leg with a mandatory Google Maps directions URL."""

    step: str = Field(..., min_length=1, description="Human-readable description of this leg")
    maps_url: str = Field(
        ...,
        min_length=1,
        description="Google Maps directions URL (https://www.google.com/maps/dir/?api=1&destination=...)",
    )

    @field_validator("maps_url")
    @classmethod
    def maps_url_must_be_valid(cls, v: str) -> str:
        """Ensure maps_url is a valid Google Maps directions URL.

        Accepts:
          - https://www.google.com/maps/dir/?api=1&destination=Place
          - https://www.google.com/maps/dir/?api=1&origin=Start&destination=End
        """
        if not _URL_PATTERN.match(v):
            raise ValueError(
                f"maps_url must be a valid Google Maps directions URL "
                f"(e.g. 'https://www.google.com/maps/dir/?api=1&destination=...'), got: {v}"
            )
        return v


class ScheduleItem(BaseModel):
    """A single scheduled item with time, action, and operational metadata.

    Designed for theme parks, museums, zoos, festivals, and any
    destination where optimizing walking, wait times, and crowd
    flow determines the quality of the day.
    """

    time: str = Field(..., min_length=1, description="Time in HH:MM AM/PM format")
    action: str = Field(..., min_length=1, description="What to do at this time (e.g. 'Rope drop Space Mountain — expect 20-min wait')")
    priority: str = Field(
        default="medium",
        description="Priority level: high, medium, or low",
        pattern=r"^(high|medium|low)$",
    )
    walking_time_min: Optional[int] = Field(
        default=None,
        ge=0,
        description="Estimated walking time in minutes from previous stop",
    )
    wait_time_min: Optional[int] = Field(
        default=None,
        ge=0,
        description="Expected wait time in minutes for this activity",
    )
    restaurant: Optional[str] = Field(
        default=None,
        description="Recommended restaurant for this meal stop (e.g. 'Be Our Guest — French, $$, inside park')",
    )
    meal_timing_note: Optional[str] = Field(
        default=None,
        description="Why this meal stop is positioned here (e.g. 'beat the noon lunch rush')",
    )
    reminder_min: Optional[int] = Field(
        default=None,
        ge=5,
        le=60,
        description="Minutes before this scheduled event to trigger a reminder (5–60 in 5-minute increments, or null for disabled)",
    )
    walking_map_url: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Google Maps walking directions URL from the previous schedule stop "
        "to this one within the venue (e.g. 'https://www.google.com/maps/dir/?api=1&origin=Congo+River+Rapids&destination=Kumba&travelmode=walking')",
    )
    backup_plan: Optional[str] = Field(
        default=None,
        description="Fallback if this activity is closed, too crowded, or weather-impacted",
    )

    @field_validator("walking_map_url")
    @classmethod
    def walking_map_url_must_be_valid(cls, v: str | None) -> str | None:
        """Validate walking map URLs use origin + destination + walking mode."""
        if v is None:
            return v
        if not _WALK_URL_PATTERN.match(v):
            raise ValueError(
                f"walking_map_url must be a valid Google Maps walking directions URL "
                f"(e.g. 'https://www.google.com/maps/dir/?api=1&origin=Ride+A&destination=Ride+B&travelmode=walking'), "
                f"got: {v}"
            )
        return v

    @field_validator("time")
    @classmethod
    def time_must_look_like_clock(cls, v: str) -> str:
        """Normalize free-form times; reject only if unparseable."""
        import re

        from app.engine.timeparse import normalize_time

        if not v or not str(v).strip():
            raise ValueError("time must not be empty")
        normalized = normalize_time(v.strip())
        if not re.match(r"^\d{1,2}:\d{2}\s*(AM|PM)", normalized, re.IGNORECASE):
            raise ValueError(
                f"time could not be parsed (e.g. '07:30 AM', '0800', '8am'), got: {v}"
            )
        return normalized


class RentalCar(BaseModel):
    """A rental car recommendation for the destination."""

    company: str = Field(..., min_length=1, description="Rental car company name (e.g. 'Hertz', 'Enterprise', 'Avis')")
    car_type: str = Field(..., min_length=1, description="Suggested vehicle type (e.g. 'Mid-size SUV', 'Economy sedan')")
    estimated_daily_rate: str = Field(..., min_length=1, description="Estimated daily rate range (e.g. '$45-65/day')")
    pickup_location: str = Field(..., min_length=1, description="Where to pick up the car (e.g. 'Denver International Airport — on-site counter')")
    booking_url: str = Field(default="https://www.kayak.com/cars", min_length=1, description="URL to book or compare rental cars")


class RideShare(BaseModel):
    """A ride share option for airport transfers or local transit."""

    service: str = Field(..., min_length=1, description="Ride share service name (e.g. 'Uber', 'Lyft')")
    route: str = Field(..., min_length=1, description="Pickup → dropoff description (e.g. 'Jacksonville International Airport → Hyatt Regency Downtown')")
    estimated_cost: str = Field(..., min_length=1, description="Estimated fare range (e.g. '$25-35')")
    estimated_time: str = Field(..., min_length=1, description="Estimated trip time (e.g. '20-25 min')")
    app_url: str = Field(default="", min_length=0, description="Deep link or web URL to open the ride share app")


class ParkingOption(BaseModel):
    """A long-term airport parking option for users driving to the airport."""

    name: str = Field(..., min_length=1, description="Parking facility name (e.g. 'JAX Economy Lot 1', 'USA Park Airport Parking')")
    type: str = Field(..., min_length=1, description="Parking type (e.g. 'Economy Lot', 'Covered Garage', 'Valet', 'Off-site Shuttle Lot')")
    daily_rate: str = Field(..., min_length=1, description="Daily parking rate (e.g. '$8/day', '$12/day')")
    shuttle: str = Field(default="Shuttle to terminal", description="Shuttle/transit info (e.g. 'Free 24/7 shuttle every 10 min')")
    location: str = Field(..., min_length=1, description="Location (e.g. 'On-site — 5 min walk to Terminal A', 'Off-site — 1.5 miles from JAX')")
    booking_url: str = Field(default="", description="URL to reserve/book parking (e.g. airport parking page or SpotHero link)")


class Flight(BaseModel):
    """A recommended airline/flight option for trips involving air travel."""

    airline: str = Field(..., min_length=1, description="Airline name (e.g. 'Delta', 'United', 'Southwest', 'American')")
    route: str = Field(..., min_length=1, description="Departure → Arrival route (e.g. 'JAX → DEN via Atlanta')")
    estimated_price: str = Field(..., min_length=1, description="Estimated price range (e.g. '$250-400 round trip')")
    flight_time: str = Field(..., min_length=1, description="Estimated flight duration (e.g. '~5h 30m including layover')")
    booking_url: str = Field(..., min_length=1, description="URL to search/book flights (e.g. 'https://www.kayak.com/flights' or airline direct link)")


class Hotel(BaseModel):
    """A recommended hotel (3+ stars only) for multi-day trips."""

    name: str = Field(..., min_length=1, description="Hotel name (e.g. 'Hyatt Regency Denver')")
    star_rating: int = Field(..., ge=3, le=5, description="Star rating (3, 4, or 5)")
    price_range: str = Field(..., min_length=1, description="Price range (e.g. '$$', '$$$')")
    location: str = Field(..., min_length=1, description="Area/neighborhood description (e.g. 'Downtown Denver — near 16th Street Mall')")
    highlights: str = Field(default="", description="Key highlights (e.g. 'Free breakfast, airport shuttle, indoor pool')")
    booking_url: str = Field(default="https://www.booking.com", min_length=1, description="URL to book or check availability")


class TravelPlan(BaseModel):
    """A complete validated travel itinerary optimized for the venue type.

    Produced by Plan-It -- an AI assistant that
    builds personalized, efficiency-optimized schedules for theme parks,
    museums, zoos, festivals, national parks, and multi-day city trips.
    """

    venue_type: str = Field(
        default="general",
        description="Venue category: theme_park, museum, zoo, festival, national_park, city_tour, general",
    )
    departure_time: str = Field(default="", description="Departure time in HH:MM AM/PM format, or empty if not specified")
    route: List[Stop] = Field(..., min_length=1, description="Ordered route legs with Google Maps URLs")
    schedule: List[ScheduleItem] = Field(..., min_length=1, description="Chronological day schedule with operational metadata")
    alerts: List[str] = Field(default_factory=list, description="Traffic, weather, closure, or crowd warnings")
    strategy_notes: List[str] = Field(
        default_factory=list,
        description="Crowd-flow tips, meal timing strategy, parking/transport recommendations",
    )
    rental_cars: List[RentalCar] = Field(
        default_factory=list,
        description="Recommended rental car options for the destination (if flying)",
    )
    ride_shares: List[RideShare] = Field(
        default_factory=list,
        description="Ride share options for airport transfers and local transit",
    )
    parking_options: List[ParkingOption] = Field(
        default_factory=list,
        description="Long-term airport parking options (if driving to airport)",
    )
    flights: List[Flight] = Field(
        default_factory=list,
        description="Recommended airline/flight options for air travel",
    )
    hotels: List[Hotel] = Field(
        default_factory=list,
        description="Recommended hotels (3+ stars) for multi-day trips",
    )
    total_walking_min: Optional[int] = Field(
        default=None,
        ge=0,
        description="Estimated total walking time in minutes across all legs",
    )
    total_wait_min: Optional[int] = Field(
        default=None,
        ge=0,
        description="Estimated total wait time in minutes across all queued activities",
    )

    @field_validator("departure_time")
    @classmethod
    def departure_time_strip(cls, v: str) -> str:
        """Strip and normalize departure_time when present."""
        import re

        from app.engine.timeparse import normalize_time

        if not v:
            return v
        normalized = normalize_time(v.strip())
        if re.match(r"^\d{1,2}:\d{2}\s*(AM|PM)", normalized, re.IGNORECASE):
            return normalized
        return v.strip()
