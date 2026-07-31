"""Crowd prediction and calendar awareness for venues.

Provides predicted crowd levels (1-10 scale).  Prefers live wait-time
data from Queue-Times.com when a venue can be matched to a supported
park and the target date is today (or omitted).  Falls back to a
recalibrated day/season/holiday heuristic otherwise.

Queue-Times attribution is required when live data is used:
https://queue-times.com/
"""

from __future__ import annotations

import json
import logging
import re
import urllib.request
from datetime import date
from functools import lru_cache

logger = logging.getLogger("plan-it.crowd")

# Queue-Times park IDs (from https://queue-times.com/parks.json) — multi-park coverage
_PARK_IDS: dict[str, int] = {
    # Walt Disney World
    "magic kingdom": 6,
    "disney magic kingdom": 6,
    "epcot": 5,
    "hollywood studios": 7,
    "disney hollywood studios": 7,
    "hollywood": 7,
    "animal kingdom": 8,
    "disney animal kingdom": 8,
    # Disneyland Resort
    "disney california adventure": 17,
    "california adventure": 17,
    "disneyland": 16,
    # Universal
    "islands of adventure": 64,
    "islands of adventure at universal orlando": 64,
    "universal studios florida": 65,
    "universal studios at universal orlando": 65,
    "universal studios orlando": 65,
    "universal studios hollywood": 66,
    "epic universe": 334,
    "volcano bay": 67,
    "universal volcano bay": 67,
    # SeaWorld / Busch
    "busch gardens tampa": 24,
    "busch gardens": 24,
    "busch gardens williamsburg": 23,
    "seaworld orlando": 21,
    "sea world orlando": 21,
    "seaworld san diego": 20,
    "sea world san diego": 20,
    "seaworld san antonio": 22,
    "aquatica orlando": 94,
    "adventure island": 97,
    "sesame place": 29,
    # Six Flags
    "six flags great adventure": 37,
    "six flags magic mountain": 32,
    "six flags over georgia": 35,
    "six flags over texas": 34,
    "six flags great america": 38,
    "six flags discovery kingdom": 33,
    "six flags fiesta texas": 39,
    "six flags new england": 43,
    "six flags st. louis": 36,
    "six flags america": 42,
    # Cedar Fair / others
    "cedar point": 50,
    "knott's berry farm": 61,
    "knotts berry farm": 61,
    "kings island": 60,
    "kings dominion": 62,
    "carowinds": 59,
    "california's great america": 57,
    "hersheypark": 15,
    "hershey park": 15,
    "dollywood": 55,
    "silver dollar city": 10,
    "legoland florida": 280,
    "legoland california": 279,
    "legoland new york": 299,
    "kennywood": 312,
}

# Resort / umbrella names → component park IDs (averaged for crowd; searched for waits)
_RESORT_PARKS: dict[str, list[int]] = {
    "walt disney world": [6, 5, 7, 8],
    "disney world": [6, 5, 7, 8],
    "wdw": [6, 5, 7, 8],
    "disneyland resort": [16, 17],
    "universal orlando": [65, 64, 334, 67],
    "universal orlando resort": [65, 64, 334, 67],
    "seaworld orlando resort": [21, 94],
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_crowd_level(venue_name: str, target_date: date | None = None) -> int:
    """Predict crowd level for a venue on a given date (1-10 scale).

    1 = empty, 5 = average, 10 = packed.
    """
    level, _source = get_crowd_level_with_source(venue_name, target_date)
    return level


def get_crowd_level_with_source(
    venue_name: str, target_date: date | None = None
) -> tuple[int, str]:
    """Return ``(level, source)`` where source is ``live`` or ``estimate``."""
    if target_date is None:
        target_date = date.today()

    # Live waits are only meaningful for "today" (park timezone ≈ visit day).
    if target_date == date.today():
        live = _live_crowd_level(venue_name)
        if live is not None:
            return live, "live"

    return _heuristic_crowd_level(venue_name, target_date), "estimate"


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
    return _holiday_adjustment(target_date) > 0


def estimate_attraction_wait(
    attraction: str,
    venue_name: str = "",
    *,
    target_date: date | None = None,
) -> dict[str, object] | None:
    """Return live wait info for an attraction string, or None if unavailable.

    Handles free-form planner strings such as:
      - ``Space Mountain``
      - ``Magic Kingdom: Space Mountain, Seven Dwarfs Mine Train``
      - ``Guardians of the Galaxy: Cosmic Rewind``

    Returns dict with:
      wait_min (int), matched (list[str]), park_ids (list[int]), source ("live")
    """
    if target_date is None:
        target_date = date.today()
    if target_date != date.today():
        return None

    park_hint, ride_names = _parse_attraction_label(attraction)
    park_ids = _resolve_park_ids(park_hint) if park_hint else []
    if not park_ids:
        park_ids = _resolve_park_ids(venue_name)
    if not park_ids:
        # Last resort: scan all known single-park aliases mentioned in the text
        blob = f"{attraction} {venue_name}".lower()
        for key, pid in sorted(_PARK_IDS.items(), key=lambda kv: -len(kv[0])):
            if key in blob and pid not in park_ids:
                park_ids.append(pid)

    if not park_ids:
        return None

    # Build ride catalog across candidate parks
    catalog: list[tuple[int, str, float]] = []  # park_id, name, wait
    for pid in park_ids:
        for name, wait in _fetch_park_ride_waits(pid):
            catalog.append((pid, name, wait))

    if not catalog:
        return None

    matched_waits: list[float] = []
    matched_names: list[str] = []
    for query in ride_names or [attraction]:
        hit = _match_ride(query, catalog)
        if hit:
            _pid, name, wait = hit
            matched_waits.append(wait)
            matched_names.append(name)

    if matched_waits:
        # Use the highest matched wait so the schedule plans for the worst line
        wait_min = int(round(max(matched_waits)))
        return {
            "wait_min": wait_min,
            "matched": matched_names,
            "park_ids": park_ids,
            "source": "live",
        }

    # No ride-level match — fall back to park average across open rides
    all_waits = [w for _pid, _n, w in catalog]
    if not all_waits:
        return None
    avg = sum(all_waits) / len(all_waits)
    return {
        "wait_min": int(round(avg)),
        "matched": [],
        "park_ids": park_ids,
        "source": "live_park_avg",
    }


def _parse_attraction_label(attraction: str) -> tuple[str, list[str]]:
    """Split ``Park: Ride A, Ride B`` into (park_hint, [rides])."""
    text = (attraction or "").split(" — ")[0].strip()
    if not text:
        return "", []

    park_hint = ""
    rides_part = text

    # "Magic Kingdom: Space Mountain, Seven Dwarfs Mine Train"
    if ":" in text:
        left, right = text.split(":", 1)
        # Only treat left as park if it looks like a park/resort name
        if _resolve_park_ids(left) or any(k in left.lower() for k in _PARK_IDS) or any(
            k in left.lower() for k in _RESORT_PARKS
        ):
            park_hint = left.strip()
            rides_part = right.strip()
        else:
            # e.g. "Guardians of the Galaxy: Cosmic Rewind" — whole string is the ride
            return "", [text]

    # Split ride list on commas / "and"
    parts = re.split(r"\s*,\s*|\s+and\s+", rides_part, flags=re.IGNORECASE)
    rides = [p.strip() for p in parts if p.strip()]
    return park_hint, rides


def _normalize_ride_key(name: str) -> str:
    """Lowercase alphanumeric key for fuzzy ride matching."""
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())


def _match_ride(
    query: str, catalog: list[tuple[int, str, float]]
) -> tuple[int, str, float] | None:
    """Best fuzzy match of *query* against live ride catalog."""
    q = _normalize_ride_key(query)
    if not q or len(q) < 3:
        return None

    # Exact normalized match
    for pid, name, wait in catalog:
        if _normalize_ride_key(name) == q:
            return pid, name, wait

    # Substring either direction (prefer longest catalog name that contains query)
    candidates: list[tuple[int, int, str, float]] = []
    for pid, name, wait in catalog:
        key = _normalize_ride_key(name)
        if q in key or key in q:
            # Prefer standard queues over Single Rider / Virtual variants
            penalty = 0
            lower = name.lower()
            if "single rider" in lower:
                penalty = 50
            elif "virtual" in lower or "lightning" in lower:
                penalty = 20
            candidates.append((len(key) - penalty, pid, name, wait))
    if candidates:
        candidates.sort(reverse=True)
        _n, pid, name, wait = candidates[0]
        return pid, name, wait

    # Token overlap: require most significant tokens
    q_tokens = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) > 2]
    if len(q_tokens) >= 2:
        best = None
        best_score = 0
        for pid, name, wait in catalog:
            name_l = name.lower()
            score = sum(1 for t in q_tokens if t in name_l)
            if score >= max(2, len(q_tokens) - 1) and score > best_score:
                best = (pid, name, wait)
                best_score = score
        if best:
            return best

    return None


# ---------------------------------------------------------------------------
# Live data (Queue-Times.com)
# ---------------------------------------------------------------------------

def _resolve_park_ids(venue_name: str) -> list[int]:
    """Map a free-form venue name to one or more Queue-Times park IDs."""
    lower = (venue_name or "").lower().strip()
    if not lower:
        return []

    # Prefer longer / more specific resort keys first
    for key, ids in sorted(_RESORT_PARKS.items(), key=lambda kv: -len(kv[0])):
        if key in lower:
            return list(ids)

    for key, pid in sorted(_PARK_IDS.items(), key=lambda kv: -len(kv[0])):
        if key in lower:
            return [pid]

    return []


def _live_crowd_level(venue_name: str) -> int | None:
    """Derive a 1-10 crowd level from live average wait times, or None."""
    park_ids = _resolve_park_ids(venue_name)
    if not park_ids:
        return None

    waits: list[float] = []
    for pid in park_ids:
        park_waits = _fetch_open_wait_times(pid)
        waits.extend(park_waits)

    if not waits:
        return None

    avg = sum(waits) / len(waits)
    level = _crowd_from_avg_wait(avg)
    logger.info(
        "Live crowd for %r: avg_wait=%.1f across %d open rides → %d/10 (parks=%s)",
        venue_name[:40], avg, len(waits), level, park_ids,
    )
    return level


def _crowd_from_avg_wait(avg_wait: float) -> int:
    """Map mean open-ride wait (minutes) to a 1–10 crowd score.

    Calibrated so ~20–25 min (typical moderate Disney day) → 5,
    not the old heuristic's summer-default 7.
    """
    if avg_wait <= 5:
        return 2
    if avg_wait <= 12:
        return 3
    if avg_wait <= 18:
        return 4
    if avg_wait <= 26:
        return 5
    if avg_wait <= 34:
        return 6
    if avg_wait <= 42:
        return 7
    if avg_wait <= 55:
        return 8
    if avg_wait <= 70:
        return 9
    return 10


@lru_cache(maxsize=64)
def _fetch_park_ride_waits(park_id: int) -> tuple[tuple[str, float], ...]:
    """Fetch (ride_name, wait_min) for open rides at a park."""
    url = f"https://queue-times.com/parks/{park_id}/queue_times.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Plan-It/0.3 (crowd)"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
    except Exception as exc:
        logger.warning("Queue-Times fetch failed for park %s: %s", park_id, exc)
        return tuple()

    rides: list[tuple[str, float]] = []
    for land in data.get("lands") or []:
        for ride in land.get("rides") or []:
            if ride.get("is_open"):
                rides.append((str(ride.get("name") or ""), float(ride.get("wait_time") or 0)))
    for ride in data.get("rides") or []:
        if ride.get("is_open"):
            rides.append((str(ride.get("name") or ""), float(ride.get("wait_time") or 0)))
    return tuple((n, w) for n, w in rides if n)


def _fetch_open_wait_times(park_id: int) -> tuple[float, ...]:
    """Open-ride wait minutes for a park (used by crowd-level averaging)."""
    return tuple(w for _name, w in _fetch_park_ride_waits(park_id))


# ---------------------------------------------------------------------------
# Heuristic fallback (recalibrated — additive, not multiplicative)
# ---------------------------------------------------------------------------

def _heuristic_crowd_level(venue_name: str, target_date: date) -> int:
    """Additive model calibrated closer to historical park averages."""
    base = _base_crowd_for_venue(venue_name)
    raw = (
        base
        + _day_of_week_adjustment(target_date)
        + _season_adjustment(target_date)
        + _holiday_adjustment(target_date)
    )
    return max(1, min(10, round(raw)))


def _base_crowd_for_venue(venue_name: str) -> float:
    """Typical mid-week, shoulder-season crowd level for a venue."""
    venue_lower = venue_name.lower()
    if any(kw in venue_lower for kw in (
        "disney", "magic kingdom", "epcot", "hollywood studios", "animal kingdom",
        "universal", "islands of adventure",
    )):
        return 5.0  # was 6.0 — overstated typical days
    if any(kw in venue_lower for kw in ("busch gardens", "sea world", "seaworld", "legoland")):
        return 4.0
    if any(kw in venue_lower for kw in ("six flags", "cedar point")):
        return 4.0
    if any(kw in venue_lower for kw in ("zoo", "aquarium", "museum")):
        return 3.0
    if any(kw in venue_lower for kw in ("national park", "yosemite", "yellowstone", "grand canyon")):
        return 4.0
    return 3.0


def _day_of_week_adjustment(d: date) -> float:
    dow = d.weekday()  # 0=Monday
    if dow in (5, 6):  # Sat/Sun
        return 1.5
    if dow in (0, 4):  # Mon/Fri
        return 0.5
    return -0.5  # Tue–Thu quieter


def _season_adjustment(d: date) -> float:
    month, day = d.month, d.day
    # Peak summer: mid-June through late July
    if month == 6 and day >= 15:
        return 1.0
    if month == 7:
        return 1.0 if day <= 25 else 0.5  # late July softens
    if month == 8 and day <= 15:
        return 0.5
    if month == 8:
        return -0.5  # back-to-school taper
    if month in (3, 4):  # spring break window
        return 1.0
    if month in (11, 12):
        return 0.5
    if month in (1, 2, 9):
        return -1.0
    return 0.0


def _holiday_adjustment(d: date) -> float:
    month, mday = d.month, d.day

    if month == 12 and mday >= 20:
        return 2.5
    if month == 1 and mday <= 3:
        return 2.0
    if month == 11 and 20 <= mday <= 30:
        return 2.0
    if month == 3 and mday >= 10:
        return 1.0
    if month == 4 and mday <= 20:
        return 1.0
    if month == 5 and mday >= 25:
        return 1.5
    if month == 7 and 1 <= mday <= 7:
        return 2.0
    if month == 9 and 1 <= mday <= 7:
        return 1.5
    if month == 2 and 13 <= mday <= 20:
        return 1.0
    if month == 1 and 13 <= mday <= 20:
        return 0.5
    if month == 10:
        return 0.5
    return 0.0


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
