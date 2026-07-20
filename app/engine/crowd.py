"""Crowd prediction and calendar awareness for venues.

Provides predicted crowd levels (1-10 scale) based on venue type,
day of week, season, and known special events.  Integrates with the
planner to optimize schedule ordering (hit high-wait attractions
early) and surface crowd-avoidance tips.

Data sources:
  - Historical crowd patterns for major US theme parks
  - School holiday calendars (spring break, summer, winter break)
  - Known conventions / events that spike attendance
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from functools import lru_cache

logger = logging.getLogger("plan-it.crowd")

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@lru_cache(maxsize=128)
def get_crowd_level(venue_name: str, target_date: date | None = None) -> int:
    """Predict crowd level for a venue on a given date (1-10 scale).

    1 = empty, 5 = average, 10 = packed.

    Args:
        venue_name: Normalized venue name.
        target_date: Date to predict.  Defaults to today.

    Returns:
        Integer 1-10.
    """
    if target_date is None:
        target_date = date.today()

    base = _base_crowd_for_venue(venue_name)
    day_mult = _day_of_week_multiplier(target_date)
    season_mult = _season_multiplier(target_date)
    holiday_mult = _holiday_multiplier(target_date)

    raw = base * day_mult * season_mult * holiday_mult
    return max(1, min(10, round(raw)))


def get_crowd_tips(venue_name: str, crowd_level: int) -> list[str]:
    """Return crowd-avoidance strategy tips for a given crowd level."""
    tips: list[str] = []

    if crowd_level >= 8:
        tips.append("⚠ Peak crowd day — arrive 60+ minutes before opening for best results")
        tips.append("⚠ Use single-rider lines where available to cut wait times 50-70%")
        tips.append("⚠ Book dining reservations in advance — walk-up waits exceed 60 min")
    elif crowd_level >= 6:
        tips.append("Busy day expected — arrive 30 minutes before opening")
        tips.append("Hit the most popular attractions in the first 2 hours")
    elif crowd_level >= 4:
        tips.append("Moderate crowds — a good day to visit")
    else:
        tips.append("Light crowds expected — a great day to explore at your own pace")

    venue_lower = venue_name.lower()

    # Venue-specific tips
    if "disney" in venue_lower or "magic kingdom" in venue_lower:
        tips.append("Use Genie+ / Lightning Lane for top-tier attractions")
        if crowd_level >= 6:
            tips.append("Book Individual Lightning Lane for Seven Dwarfs Mine Train and TRON")
    elif "universal" in venue_lower:
        tips.append("Express Pass recommended on crowd levels 6+")
    elif "busch gardens" in venue_lower:
        tips.append("Quick Queue pass pays for itself on levels 6+")
    elif "sea world" in venue_lower or "seaworld" in venue_lower:
        tips.append("Reserved seating for shows available via Quick Queue")

    return tips


def get_seasonal_events(month: int) -> list[dict[str, str]]:
    """Return known seasonal events happening in a given month (1-12)."""
    events: list[dict[str, str]] = []
    monthly = _SEASONAL_EVENTS.get(month, [])
    for e in monthly:
        events.append(dict(e))
    return events


def is_holiday_period(target_date: date | None = None) -> bool:
    """Return True if the date falls within a known high-crowd holiday period."""
    if target_date is None:
        target_date = date.today()
    return _holiday_multiplier(target_date) > 1.0


# ---------------------------------------------------------------------------
# Internal multipliers
# ---------------------------------------------------------------------------

def _base_crowd_for_venue(venue_name: str) -> float:
    """Default average crowd level for a venue type."""
    venue_lower = venue_name.lower()
    # Major theme parks have higher baseline crowds
    if any(kw in venue_lower for kw in (
        "disney", "magic kingdom", "epcot", "hollywood studios", "animal kingdom",
        "universal", "islands of adventure",
    )):
        return 6.0
    if any(kw in venue_lower for kw in ("busch gardens", "sea world", "seaworld", "legoland")):
        return 4.5
    if any(kw in venue_lower for kw in ("six flags", "cedar point")):
        return 4.0
    if any(kw in venue_lower for kw in ("zoo", "aquarium", "museum")):
        return 3.5
    if any(kw in venue_lower for kw in ("national park", "yosemite", "yellowstone", "grand canyon")):
        return 4.0
    return 3.0


def _day_of_week_multiplier(d: date) -> float:
    """Weekends and Mondays/Fridays are busier."""
    dow = d.weekday()  # 0=Monday, 6=Sunday
    if dow in (5, 6):  # Saturday, Sunday
        return 1.4
    if dow in (0, 4):  # Monday, Friday
        return 1.15
    return 0.85  # Tuesday–Thursday are quietest


def _season_multiplier(d: date) -> float:
    """Seasonal crowd variation."""
    month = d.month
    # Summer (June–August): peak
    if month in (6, 7, 8):
        return 1.3
    # Spring break window (March–April)
    if month in (3, 4):
        return 1.2
    # Holiday season (Nov–Dec)
    if month in (11, 12):
        return 1.15
    # Shoulder seasons
    if month in (5, 9, 10):
        return 0.95
    # Dead season (Jan–Feb)
    return 0.75


def _holiday_multiplier(d: date) -> float:
    """Holiday-specific crowd spikes."""
    month = d.month
    mday = d.day
    # Use weekday() indirectly through known holiday periods

    # Christmas / New Year week
    if month == 12 and mday >= 20:
        return 1.6
    if month == 1 and mday <= 3:
        return 1.5

    # Thanksgiving week (4th Thursday of November)
    if month == 11 and 20 <= mday <= 30:
        return 1.4

    # Spring break (mid-March through mid-April)
    if month == 3 and mday >= 10:
        return 1.3
    if month == 4 and mday <= 20:
        return 1.3

    # Memorial Day weekend (late May)
    if month == 5 and mday >= 25:
        return 1.2

    # July 4th week
    if month == 7 and 1 <= mday <= 7:
        return 1.3

    # Labor Day weekend (early September)
    if month == 9 and 1 <= mday <= 7:
        return 1.2

    # Presidents' Day weekend (mid-February)
    if month == 2 and 13 <= mday <= 20:
        return 1.15

    # MLK Day weekend (mid-January)
    if month == 1 and 13 <= mday <= 20:
        return 1.1

    # Halloween season at theme parks (October)
    if month == 10:
        return 1.1

    return 1.0


# Known seasonal events by month (US-focused)
_SEASONAL_EVENTS: dict[int, list[dict[str, str]]] = {
    1: [
        {"name": "New Year's Day", "impact": "High crowds at theme parks, many businesses closed"},
        {"name": "MLK Day Weekend", "impact": "Moderate theme park crowds"},
    ],
    2: [
        {"name": "Presidents' Day Weekend", "impact": "Busy at theme parks, especially Disney/Universal"},
        {"name": "Mardi Gras (varies)", "impact": "Peak crowds in New Orleans, moderate elsewhere"},
    ],
    3: [
        {"name": "Spring Break Season Begins", "impact": "Crowds build through March at all Florida/CA parks"},
        {"name": "St. Patrick's Day", "impact": "Busy at bars and city-tour venues"},
    ],
    4: [
        {"name": "Spring Break Peak", "impact": "Peak season at all theme parks and beaches"},
        {"name": "Easter (varies)", "impact": "Very high crowds when aligned with spring break"},
    ],
    5: [
        {"name": "Memorial Day Weekend", "impact": "Summer crowds begin — busy at all outdoor venues"},
        {"name": "Graduation Season", "impact": "Hotel prices spike in college towns"},
    ],
    6: [
        {"name": "Summer Peak Begins", "impact": "All venues at high capacity — book ahead"},
        {"name": "Pride Month Events", "impact": "City-tour venues busier in major metros"},
    ],
    7: [
        {"name": "Independence Day (July 4)", "impact": "Peak crowds, fireworks events, heavy traffic"},
        {"name": "Summer Peak", "impact": "Hottest temps, highest crowds at all outdoor venues"},
    ],
    8: [
        {"name": "Summer Peak Continues", "impact": "Hot, crowded — go early and hydrate"},
        {"name": "Back to School", "impact": "Crowds taper late August as schools resume"},
    ],
    9: [
        {"name": "Labor Day Weekend", "impact": "Last summer hurrah — busy at beaches and parks"},
        {"name": "Halloween Horror Nights Begin", "impact": "Universal Studios Florida — evenings very busy"},
    ],
    10: [
        {"name": "Halloween Season", "impact": "Theme parks busy with Halloween events on weekends"},
        {"name": "Fall Festivals", "impact": "State fairs, Oktoberfests, harvest festivals nationwide"},
    ],
    11: [
        {"name": "Thanksgiving Week", "impact": "Peak travel week — airports packed, theme parks very busy"},
        {"name": "Veterans Day Weekend", "impact": "Moderate crowds at national parks (free entry day)"},
    ],
    12: [
        {"name": "Christmas / Holiday Season", "impact": "Peak crowds Dec 20–31 at all attractions"},
        {"name": "New Year's Eve", "impact": "Maximum crowds, premium pricing, book everything in advance"},
    ],
}
