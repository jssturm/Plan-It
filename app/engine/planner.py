"""Deterministic itinerary builder — replaces LLM prompt with rules engine.

Uses search results from app.engine.search to assemble a complete
TravelPlan without any cloud LLM dependency. Produces the same
Pydantic-validated output schema consumed by the frontend.
"""

from __future__ import annotations

import logging
import random
import re
import urllib.parse
from datetime import date

from dateutil.parser import parse as parse_date
from dateutil.parser import ParserError

from app.engine import crowd, currency, search, weather
from app.engine.addressparse import normalize_us_address
from app.engine.timeparse import fmt_time as _fmt_time
from app.engine.timeparse import normalize_time as _normalize_departure_time
from app.engine.timeparse import parse_time as _parse_time
from app.llm import deepseek_client

logger = logging.getLogger("plan-it.planner")

# ---------------------------------------------------------------------------
# Core plan builder — public API
# ---------------------------------------------------------------------------


def build_travel_plan(
    user_input: str,
    starting_location: str | None = None,
    restaurant_preferences: str | None = None,
    departure_time: str | None = None,
    default_reminder_min: int | None = None,
) -> dict:
    """Given a natural-language trip description, return a validated TravelPlan dict.

    No LLM required — uses DuckDuckGo search + deterministic rules.

    Args:
        user_input: Raw user text describing the trip.
        starting_location: Optional departure point.
        restaurant_preferences: Optional dietary/cuisine preferences.

    Returns:
        A dict matching the TravelPlan schema (app.schemas.itinerary.TravelPlan).
    """
    # 1. Parse the user's intent — LLM-first with regex fallback
    intent = _parse_intent_llm(user_input)

    # 1a. Extract date from user input ("tomorrow", "next Saturday", etc.)
    trip_date = _extract_date_from_input(user_input)

    # Merge inferred starting location from free-text ("from X")
    # with the explicit API field, preferring the explicit one.
    if not starting_location and intent.get("starting_location"):
        starting_location = intent["starting_location"]

    # 2. Research the venue — include location for accurate results
    search_venue_name = intent["venue"]
    if intent.get("location"):
        search_venue_name = f"{intent['venue']} {intent['location']}"

    venue = search.search_venue_info(search_venue_name)

    # 3. Build the route legs (pass departure_time for meal-label context)
    # Normalize free-form starting addresses so Census geocoding gets structure.
    if starting_location:
        starting_location = normalize_us_address(starting_location)
    route = _build_route(intent, venue, starting_location, user_input,
                         departure_time=departure_time)

    # 4. Detect multi-day trip from text signals AND drive distance
    is_multiday = _detect_multiday(user_input, route, intent, starting_location)

    # 5. Determine departure time (user-provided only; no auto-population)
    if departure_time:
        final_departure = _normalize_departure_time(departure_time)
    else:
        final_departure = ""

    # 6. Build the schedule
    schedule = _build_schedule(intent, venue, route, is_multiday, starting_location,
                               departure_time=final_departure)

    # 7. Research restaurants — include location for accurate results
    venue_area = f"near {intent['venue']}"
    if intent.get("location"):
        venue_area = f"near {intent['venue']} {intent['location']}"
    restaurants = search.search_restaurants(venue_area, restaurant_preferences or "", count=6)

    # For multi-day trips, also search for restaurants along the return route
    if is_multiday and starting_location:
        dest_name = intent["venue"]
        if intent.get("location"):
            dest_name = f"{intent['venue']} {intent['location']}"
        midpoint = _infer_midpoint(dest_name, starting_location)
        # Return-route restaurants for Day 2
        ret_restaurants = search.search_restaurants(
            f"near {midpoint}", restaurant_preferences or "", count=3
        )
        # Prepend so they get used for Day 2 lunch first
        ret_restaurants.extend(restaurants)
        restaurants = ret_restaurants

    # 7a. Apply default reminder to all schedule items
    if default_reminder_min:
        for item in schedule:
            if item.get("reminder_min") is None:
                item["reminder_min"] = default_reminder_min

    # 8. Inject restaurant recommendations into schedule items
    schedule = _inject_restaurants(schedule, restaurants, restaurant_preferences)

    # 8a. Crowd prediction — venue-specific crowd level and tips
    crowd_level = 5  # default: average
    try:
        crowd_level = crowd.get_crowd_level(intent["venue"])
        crowd_tips = crowd.get_crowd_tips(intent["venue"], crowd_level)
        if crowd_tips:
            strategy = list(crowd_tips) + strategy
    except Exception:
        logger.warning("Crowd prediction failed, using defaults", exc_info=True)

    # 8b. Weather forecast — free Open-Meteo API (non-critical)
    try:
        weather_ctx = weather.weather_summary_for_plan(
            intent["venue"], intent.get("location", "")
        )
        if weather_ctx:
            strategy.append(weather_ctx["note"])
            for alert in weather_ctx.get("alerts", []):
                alerts.append(alert)
            for pack in weather_ctx.get("packing", []):
                strategy.append(f"Pack: {pack}")
    except Exception:
        logger.warning("Weather lookup failed, continuing without forecast", exc_info=True)

    # 9. Assemble the full plan

    total_walking = sum(s.get("walking_time_min", 0) or 0 for s in schedule)
    total_wait = sum(s.get("wait_time_min", 0) or 0 for s in schedule)

    # Map venue info to alerts and strategy notes
    alerts = list(venue.get("alerts", []))
    strategy = list(venue.get("crowd_tips", [])[:3])
    if venue.get("parking_info"):
        strategy.append(f"Parking: {venue['parking_info'][:120]}")

    # Transit alerts
    transit_warnings: list[str] = []
    for leg in route:
        if traffic_warning := _check_traffic_warning(leg.get("step", "")):
            transit_warnings.append(traffic_warning)
    alerts.extend(transit_warnings[:3])

    # De-duplicate alerts (keep first occurrence order)
    seen_alerts: set[str] = set()
    unique_alerts: list[str] = []
    for a in alerts:
        if a.lower() not in seen_alerts:
            seen_alerts.add(a.lower())
            unique_alerts.append(a)
    alerts = unique_alerts

    # Hotels for multi-day — use location for accurate results
    hotels: list[dict] = []
    if is_multiday:
        hotel_area = intent.get("location") or intent["venue"]
        hotels = search.search_hotels(hotel_area, count=3)

    # Flights for long / undriveable trips.
    # Triggered when ANY of these are true:
    #   1. One-way drive > 6 hours (most people fly for 6h+ drives)
    #   2. User mentions flying/ferry/boat/train ("fly to", "flight", "ferry", etc.)
    #   3. No drive-time estimate available (likely international / cross-continent)
    total_drive_h = _estimate_total_drive(route)
    user_wants_flight = _user_mentioned_flying(user_input)
    needs_flight = (
        (total_drive_h > 6 and starting_location)
        or user_wants_flight
        or (total_drive_h == 0 and starting_location and _route_looks_undriveable(route))
    )

    flights: list[dict] = []
    rental_cars: list[dict] = []
    ride_shares: list[dict] = []
    parking_options: list[dict] = []
    if needs_flight:
        dest_location = intent.get("location") or intent["venue"]
        origin = starting_location or "your location"
        flights = _default_flights(origin, dest_location)
        rental_cars = search.search_rental_cars(dest_location)
        ride_shares = search.search_ride_shares(origin, dest_location)
        if starting_location:
            parking_options = _default_parking(starting_location)

        # International travel tips — when origin/destination look like different countries
        if _looks_international(origin, dest_location):
            strategy.append("🛂 International travel: ensure passports are valid for 6+ months beyond your return date")
            strategy.append("💱 Check exchange rates and notify your bank of travel dates")
            alerts.append("✈ International flight — arrive at the airport 3 hours before departure")

    plan = {
        "venue_type": venue.get("venue_type", "general"),
        "departure_time": final_departure,
        "route": route,
        "schedule": schedule,
        "alerts": alerts[:5],
        "strategy_notes": strategy[:4],
        "rental_cars": rental_cars,
        "ride_shares": ride_shares,
        "parking_options": parking_options,
        "flights": flights,
        "hotels": hotels,
        "trip_date": trip_date.isoformat() if trip_date else "",
        "crowd_level": crowd_level,
        "total_walking_min": total_walking or None,
        "total_wait_min": total_wait or None,
    }

    logger.info(
        "Plan built: %s, %d route legs, %d schedule items, type=%s, multiday=%s, crowd=%d",
        intent["venue"][:40],
        len(route),
        len(schedule),
        venue.get("venue_type"),
        is_multiday,
        crowd_level,
    )
    return plan


# ---------------------------------------------------------------------------
# Multi-day detection
# ---------------------------------------------------------------------------


def _detect_multiday(
    user_input: str,
    route: list[dict],
    intent: dict[str, str],
    starting_location: str | None,
) -> bool:
    """Detect whether this trip spans multiple days.

    Uses both drive distance and explicit text signals like
    'hotel', 'next day', 'drive back', 'stay overnight', etc.
    """
    text_lower = user_input.lower()

    # Text signals — user explicitly mentions overnight stay
    multiday_keywords = [
        "hotel", "stay overnight", "overnight", "next day",
        "drive back", "return trip", "drive home", "the next morning",
        "spend the night", "check in", "check-in", "motel",
        "inn", "lodging", "sleep", "back the next day",
    ]
    has_text_signal = any(kw in text_lower for kw in multiday_keywords)

    # Drive distance — round trip > 4 hours implies multi-day
    total_drive_h = _estimate_total_drive(route)
    # The route is one-way, so double it for round-trip estimate
    round_trip_h = total_drive_h * 2
    is_long_round_trip = round_trip_h > 4

    # Explicit destination distance (e.g. JAX→Tampa ≈ 3h each way)
    if starting_location and intent.get("location"):
        dest = f"{intent['venue']} {intent['location']}"
        transit = search.search_transit(starting_location, dest)
        drive_str = transit.get("driving_time", "")
        one_way_min = _parse_minutes(drive_str)
        if one_way_min > 120:  # > 2 hours one-way
            is_long_round_trip = True

    return has_text_signal or is_long_round_trip


def _parse_minutes(drive_str: str) -> int:
    total = 0
    h_match = re.search(r'(\d+)\s*hour', drive_str)
    m_match = re.search(r'(\d+)\s*min', drive_str)
    if h_match:
        total += int(h_match.group(1)) * 60
    if m_match:
        total += int(m_match.group(1))
    return total if total > 0 else 0


# ---------------------------------------------------------------------------
# Intent parsing — extract venue, location, date from free text
# ---------------------------------------------------------------------------

# Sorted longest-first so "travel to" matches before "to", "day at" before "at", etc.
# Only includes phrases that directly precede a venue name — no standalone noise words.
_VENUE_INDICATORS = sorted([
    "travel to ", "going to ", "head to ", "trip to ", "day at ",
    "explore ", "visit ", "tour ", "at ",
], key=lambda x: -len(x))

_PARK_NAMES: dict[str, str] = {
    "disney": "Walt Disney World",
    "disney world": "Walt Disney World",
    "disneyland": "Disneyland",
    "magic kingdom": "Magic Kingdom",
    "epcot": "Epcot",
    "hollywood studios": "Disney's Hollywood Studios",
    "animal kingdom": "Disney's Animal Kingdom",
    "universal": "Universal Studios",
    "islands of adventure": "Universal Islands of Adventure",
    "busch gardens": "Busch Gardens",
    "sea world": "SeaWorld",
    "seaworld": "SeaWorld",
    "legoland": "Legoland",
    "six flags": "Six Flags",
    "cedar point": "Cedar Point",
    "kennedy space center": "Kennedy Space Center",
    "smithsonian": "Smithsonian",
    "louvre": "The Louvre",
    "met": "The Metropolitan Museum of Art",
    "metropolitan museum": "The Metropolitan Museum of Art",
    "san diego zoo": "San Diego Zoo",
    "bronx zoo": "Bronx Zoo",
    "yellowstone": "Yellowstone National Park",
    "yosemite": "Yosemite National Park",
    "grand canyon": "Grand Canyon National Park",
    "zion": "Zion National Park",
    "great smoky mountains": "Great Smoky Mountains National Park",
    "rocky mountain": "Rocky Mountain National Park",
    "acadia": "Acadia National Park",
    "glacier": "Glacier National Park",
    "arches": "Arches National Park",
    "bryce canyon": "Bryce Canyon National Park",
    "joshua tree": "Joshua Tree National Park",
    "olympic": "Olympic National Park",
    "everglades": "Everglades National Park",
    "shenandoah": "Shenandoah National Park",
}

# Known venue location suffixes that disambiguate multi-location venues.
# Maps the normalized park key to known city/region suffixes.
_VENUE_LOCATIONS: dict[str, list[str]] = {
    "busch gardens": ["Tampa", "Williamsburg"],
    "six flags": ["Magic Mountain", "Great America", "Over Texas", "Fiesta Texas",
                  "Great Adventure", "New England", "St. Louis", "America",
                  "Discovery Kingdom", "Over Georgia", "Mexico", "Hurricane Harbor"],
    "universal": ["Orlando", "Hollywood", "Singapore", "Japan", "Beijing"],
    "sea world": ["Orlando", "San Diego", "San Antonio"],
    "seaworld": ["Orlando", "San Diego", "San Antonio"],
    "legoland": ["California", "Florida", "New York"],
    "disney": ["World", "Land", "Orlando", "Florida", "California", "Anaheim",
               "Paris", "Tokyo", "Hong Kong", "Shanghai"],
    "disney world": ["Orlando", "Florida"],
    "six flags over georgia": ["Atlanta", "Georgia"],
}


def _parse_intent_llm(user_input: str) -> dict[str, str]:
    """Parse natural-language input using LLM with regex fallback.

    Tries DeepSeek LLM first for high-quality structured extraction.
    Falls back to the deterministic regex parser if the LLM is
    unavailable or fails.
    """
    if deepseek_client.is_available():
        try:
            llm_result = deepseek_client.parse_travel_intent(user_input)
            if llm_result.get("confidence", 0) >= 0.5:
                return {
                    "venue": llm_result.get("venue", user_input),
                    "location": llm_result.get("location", ""),
                    "time_of_day": llm_result.get("time_of_day", "morning"),
                    "raw": user_input,
                    "starting_location": llm_result.get("starting_location", ""),
                    "is_multiday": llm_result.get("is_multiday", False),
                    "restaurant_preferences": llm_result.get("restaurant_preferences", ""),
                }
            logger.info("LLM confidence too low (%.2f), falling back to regex", llm_result.get("confidence", 0))
        except Exception as exc:
            logger.warning("LLM intent parsing failed: %s", exc)

    return _parse_intent_regex(user_input)


def _parse_intent(user_input: str) -> dict[str, str]:
    """Parse natural-language input into structured intent. (Delegates to LLM-first parser.)"""
    return _parse_intent_llm(user_input)


def _parse_intent_regex(user_input: str) -> dict[str, str]:
    """Deterministic regex-based intent parser — fallback when LLM unavailable.

    Handles city-qualified venues like "Busch Gardens Tampa" by preserving
    the city suffix as the location. Also detects "near X", "in X",
    "around X", and "from X" patterns.

    Returns dict with: venue, location, time_of_day, raw, starting_location.
    """
    text = user_input.strip()
    text_lower = text.lower()

    # 0. Extract "from X" / "leaving from X" patterns BEFORE venue extraction,
    #    so the origin address doesn't interfere with venue parsing.
    #    For addresses, we look for a street-number pattern and try to grab
    #    the full address including city/state/zip.
    inferred_start: str = ""
    for marker in (" from ", " leaving from ", " departing from "):
        if marker in text_lower:
            after_from = text_lower.split(marker, 1)[-1]
            # Try to extract a full address (digits + street + city + state + zip pattern)
            addr_match = re.search(
                r'(\d+\s+[\w\s]+(?:dr|drive|st|street|ave|avenue|rd|road|blvd|blvd\.|ln|lane|ct|court|way|cir|circle|pl|place|trl|trail)\.?\s*,?\s*[\w\s]+,\s*[a-z]{2}\s*\d{5}(?:-\d{4})?)',
                after_from, re.IGNORECASE,
            )
            if addr_match:
                candidate = addr_match.group(1).strip()
            else:
                # Fallback: grab text until a stop-word, keeping commas for addresses
                candidate = (
                    after_from.split(" tomorrow")[0]
                    .split(" today")[0]
                    .split(" with ")[0]
                    .split(" and I ")[0]
                    .split(" and i ")[0]
                    .split(". I ")[0]
                    .split(". i ")[0]
                    .strip()
                )
            if candidate and len(candidate) > 2:
                # Strip noise prefixes like "my house", "my home", "home"
                candidate = _strip_address_noise(candidate)
                inferred_start = candidate.title() if candidate else ""
            break

    # 1. Extract venue name via indicator phrases.
    #    First isolate the sentence containing the venue to avoid trailing noise.
    venue = text  # fallback
    for indicator in _VENUE_INDICATORS:
        if indicator in text_lower:
            after = text.split(indicator, 1)[-1].strip()
            # Truncate at sentence boundaries before applying word-level splits
            first_sentence = (
                after.split(". ")[0]
                .split("! ")[0]
                .split("? ")[0]
            )
            venue = (
                first_sentence.split(",")[0]
                .split(" tomorrow")[0]
                .split(" today")[0]
                .split(" this")[0]
                .split(" with")[0]
                .split(" from ")[0]
                .split(" and ")[0]
                .split(" via ")[0]
                .split(" by ")[0]
                .strip()
            )
            break

    venue_lower = venue.lower()

    # 2. Match known venues and extract city suffix
    venue_normalized = venue
    location = ""

    for known, full_name in sorted(_PARK_NAMES.items(), key=lambda x: -len(x[0])):
        if known in venue_lower:
            venue_normalized = full_name
            # Extract everything after the known name as potential location
            idx = venue_lower.find(known) + len(known)
            remainder = venue[idx:].strip()

            if remainder:
                # Check if remainder matches a known location suffix
                matched_location = _match_location_suffix(known, remainder)
                if matched_location:
                    location = matched_location
                else:
                    # Treat single-word remainders as locations, filter noise
                    location = _clean_location_remainder(remainder)

            # Also check the full original text for known location suffixes
            if not location and known in _VENUE_LOCATIONS:
                for suffix in _VENUE_LOCATIONS[known]:
                    if suffix.lower() in text_lower:
                        location = suffix
                        break
            break

    # 3. Preposition-based fallback ("near X", "in X", "around X")
    if not location:
        for indicator in (" near ", " in ", " around "):
            if indicator in text_lower:
                after = text_lower.split(indicator, 1)[-1]
                candidate = (
                    after.split(",")[0]
                    .split(" tomorrow")[0]
                    .split(" with")[0]
                    .strip()
                )
                if candidate and candidate not in {"the", "a", "an", "orlando", "florida"}:
                    location = candidate.title()
                break

    # 4. Time-of-day hint — morning indicators take priority;
    #    "evening" or "dinner" only wins when there's no counter-evidence
    #    that the user intends a daytime activity.
    time_of_day = "morning"
    has_morning = any(w in text_lower for w in ("morning", "breakfast", "early", "day trip", "sunrise", "dawn"))
    has_afternoon = any(w in text_lower for w in ("afternoon", "noon", "lunch"))
    has_evening = any(w in text_lower for w in ("evening", "dinner", "night"))

    if has_morning:
        time_of_day = "morning"
    elif has_afternoon:
        time_of_day = "afternoon"
    elif has_evening:
        time_of_day = "evening"
    # else stays "morning"

    return {
        "venue": venue_normalized,
        "location": location,
        "time_of_day": time_of_day,
        "raw": user_input,
        "starting_location": inferred_start,
    }


def _match_location_suffix(known_key: str, remainder: str) -> str | None:
    """If remainder matches a known location suffix for this venue, return it."""
    if known_key not in _VENUE_LOCATIONS:
        return None
    remainder_lower = remainder.lower()
    for suffix in _VENUE_LOCATIONS[known_key]:
        if suffix.lower() in remainder_lower:
            return suffix
    return None


def _extract_date_from_input(user_input: str) -> date | None:
    """Parse date references like 'tomorrow', 'next Saturday', 'July 4th'.

    Uses python-dateutil for fuzzy parsing.  Returns a date object or None.
    """
    text_lower = user_input.lower().strip()

    # Handle relative dates that dateutil struggles with
    today = date.today()
    relative_map = {
        "tomorrow": today.replace(day=today.day + 1) if today.day < 28 else today,
        "today": today,
        "next week": today.replace(day=today.day + 7) if today.day < 22 else today,
        "this weekend": today,  # approximate
    }
    # More precise relative handling
    if "tomorrow" in text_lower:
        from datetime import timedelta
        return today + timedelta(days=1)
    if "day after tomorrow" in text_lower:
        from datetime import timedelta
        return today + timedelta(days=2)

    # Try dateutil for "next Saturday", "July 4th", "2024-12-25", etc.
    try:
        parsed = parse_date(user_input, fuzzy=True, default= today)
        if parsed:
            return parsed.date()
    except (ParserError, ValueError, OverflowError):
        pass

    return None


def _strip_address_noise(text: str) -> str:
    """Remove noise prefixes from extracted addresses like 'my house', 'home', etc."""
    noise_prefixes = [
        "my house ", "my home ", "my place ", "our house ", "our home ",
        "home ", "house ", "my ", "our ",
    ]
    text_lower = text.lower()
    for prefix in noise_prefixes:
        if text_lower.startswith(prefix):
            return text[len(prefix):].strip()
    return text


def _clean_location_remainder(remainder: str) -> str:
    """Clean up a location remainder, filtering noise words."""
    noise = {
        "tomorrow", "today", "with", "and", "for", "from", "the",
        "next", "week", "weekend", "morning", "afternoon", "evening",
        "lunch", "dinner", "trip", "plan", "park", "a", "an",
        "studios", "museums", "museum", "gallery", "gardens",
        "world", "land", "center", "space",
    }
    words = remainder.lower().split()
    filtered = [w for w in words if w not in noise]
    if not filtered:
        return ""
    return filtered[0].title() if filtered else ""


# ---------------------------------------------------------------------------
# Route construction
# ---------------------------------------------------------------------------


def _build_route(
    intent: dict[str, str],
    venue: dict,
    starting_location: str | None,
    user_input: str = "",
    departure_time: str | None = None,
) -> list[dict]:
    """Build ordered route legs with Google Maps URLs.

    For drives > 1 hour, inserts an en-route breakfast/coffee stop
    at the geographic midpoint rather than at the origin.
    """
    destination = intent["venue"]
    if intent.get("location"):
        destination = f"{intent['venue']} {intent['location']}"

    origin = starting_location or "your starting location"

    route: list[dict] = []

    if starting_location:
        # Only attempt real routing when a concrete starting location
        # is provided. "your starting location" is not a geocodeable address.
        transit = search.search_transit(starting_location, destination)
        driving_time = transit.get("driving_time", "").strip()

        step_prefix = f"Drive from {starting_location} to {destination}"
        if driving_time and driving_time[0].isdigit():
            step_text = f"{step_prefix} — approximately {driving_time}"
        else:
            step_text = f"{step_prefix} — open map for driving directions"
        route.append({
            "step": step_text,
            "maps_url": transit.get(
                "maps_url",
                f'https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(destination, safe="")}',
            ),
        })
    else:
        # No starting location — provide a generic route entry with
        # directions to the destination only.
        maps_url = f'https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(destination, safe="")}'
        route.append({
            "step": f"Head to {destination} — get directions via the map link below",
            "maps_url": maps_url,
        })

    # Rest stops every ~4 hours for long drives, plus breakfast/coffee for early starts
    drive_min = _estimate_drive_minutes(route[0].get("step", ""))
    user_wants_breakfast = "breakfast" in user_input.lower() or "coffee" in user_input.lower()

    # Compute 24-hour departure hour for meal-label context
    dep_h_24 = _parse_time(departure_time or "07:00 AM")[0]

    if starting_location:
        # Insert rest stops at 4-hour intervals (every ~240 min of driving)
        stop_hour_mark = 240  # 4 hours in minutes
        stop_counter = 0
        cumulative_min = 0
        # Pre-calculate all stop positions before the final leg
        while cumulative_min + stop_hour_mark < drive_min:
            cumulative_min += stop_hour_mark
            stop_counter += 1
            hours_in = cumulative_min // 60
            midpoint = _infer_midpoint(origin, destination)

            # Label stops by time-of-day meal context:
            #   Every 4–6 hours ≈ breakfast/brunch → lunch → dinner.
            #   Departure hour + cumulative drive hours determines which meal.
            _now = (dep_h_24 + hours_in) % 24
            if _now < 11:
                meal_label = "Brunch / coffee break"
            elif _now < 15:
                meal_label = "Lunch"
            else:
                meal_label = "Dinner"

            maps_query = _maps_search_location(midpoint, destination, origin)
            route.append({
                "step": f"{meal_label} stop ~{hours_in}h in near {midpoint} — {meal_label.lower()}, stretch your legs, ~30 min",
                "maps_url": f'https://www.google.com/maps/search/restaurants+near+{maps_query}',
            })
        # If no 4h stops were added but it's over 1h, inject a midpoint break
        if stop_counter == 0 and drive_min > 60:
            midpoint = _infer_midpoint(origin, destination)
            maps_query = _maps_search_location(midpoint, destination, origin)
            route.append({
                "step": f"Breakfast stop en route near {midpoint} — stretch, coffee, and a quick bite, ~20 min",
                "maps_url": f'https://www.google.com/maps/search/breakfast+near+{maps_query}',
            })
    elif user_wants_breakfast:
        route.append({
            "step": f"Quick coffee and breakfast stop before hitting the road — 15 minutes",
            "maps_url": f'https://www.google.com/maps/search/breakfast+near+{urllib.parse.quote(origin, safe="")}',
        })

    return route


def _infer_midpoint(origin: str, destination: str) -> str:
    """Heuristically guess a midpoint city between origin and destination."""
    combined = f"{origin} {destination}".lower()

    # Known midpoint cities for common Florida routes
    midpoint_map: dict[tuple[str, str], str] = {
        ("jacksonville", "tampa"): "Gainesville",
        ("jacksonville", "orlando"): "Daytona Beach",
        ("orlando", "tampa"): "Lakeland",
        ("orlando", "miami"): "West Palm Beach",
        ("tampa", "miami"): "Fort Myers",
        ("miami", "orlando"): "West Palm Beach",
        ("jacksonville", "busch gardens"): "Gainesville",
        ("orlando", "busch gardens"): "Lakeland",
        ("atlanta", "orlando"): "Valdosta",
        ("atlanta", "tampa"): "Valdosta",
        ("tampa", "atlanta"): "Valdosta",
        ("orlando", "atlanta"): "Valdosta",
    }

    origin_slug = origin.lower().split(",")[0].strip()
    dest_slug = destination.lower().split(",")[0].strip()

    # Direct lookup
    if (origin_slug, dest_slug) in midpoint_map:
        return midpoint_map[(origin_slug, dest_slug)]
    if (dest_slug, origin_slug) in midpoint_map:
        return midpoint_map[(dest_slug, origin_slug)]

    # Substring match
    for (a, b), city in midpoint_map.items():
        if a in origin_slug and b in dest_slug:
            return city
        if a in dest_slug and b in origin_slug:
            return city

    return "the halfway point"


def _maps_search_location(midpoint: str, fallback_destination: str, origin: str = "") -> str:
    """Return a URL-encoded location string for Google Maps URLs.

    When the midpoint heuristic returns 'the halfway point' (unknown):

    1. If *origin* is provided, computes the actual geographic midpoint
       between origin and destination via Nominatim geocoding.
    2. Otherwise, falls back to *fallback_destination* so Google Maps
       opens a meaningful location instead of the user's current position.

    Uses ``urllib.parse.quote`` for proper encoding of special characters
    (commas, ampersands, etc.) that ``.replace(' ', '+')`` would miss.
    """
    if midpoint != "the halfway point":
        return urllib.parse.quote(midpoint, safe="")

    # Try geographic midpoint computation when origin is available
    if origin:
        geo_mid = _geographic_midpoint(origin, fallback_destination)
        if geo_mid:
            return urllib.parse.quote(geo_mid, safe="")

    # Last resort: fall back to destination
    return urllib.parse.quote(fallback_destination, safe="")


def _geographic_midpoint(origin: str, destination: str) -> str | None:
    """Compute the geographic midpoint between two location names.

    Uses Nominatim to geocode both locations, calculates the midpoint
    lat/lon, then reverse-geocodes to find the nearest city/town name.

    Returns a city/region name string, or None if geocoding fails.
    """
    import json
    import time
    import urllib.request

    # ── Geocode origin ─────────────────────────────────────────────────
    time.sleep(1.2)  # Nominatim rate limit: 1 req/s
    origin_coords = _geocode_nominatim(origin)
    if not origin_coords:
        logger.info("Geographic midpoint: could not geocode origin %r", origin[:60])
        return None

    # ── Geocode destination ────────────────────────────────────────────
    time.sleep(1.2)
    dest_coords = _geocode_nominatim(destination)
    if not dest_coords:
        logger.info("Geographic midpoint: could not geocode destination %r", destination[:60])
        return None

    # ── Compute midpoint ───────────────────────────────────────────────
    mid_lat = (origin_coords[0] + dest_coords[0]) / 2.0
    mid_lon = (origin_coords[1] + dest_coords[1]) / 2.0

    # ── Reverse geocode the midpoint to a city name ────────────────────
    time.sleep(1.2)
    params = urllib.parse.urlencode({
        "lat": str(mid_lat),
        "lon": str(mid_lon),
        "format": "json",
        "zoom": 10,  # City/town level
    })
    url = f"https://nominatim.openstreetmap.org/reverse?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Plan-It/0.3"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
    except Exception as exc:
        logger.warning("Reverse geocode failed for (%.4f, %.4f): %s", mid_lat, mid_lon, exc)
        return None

    # Extract city, town, or county name from the Nominatim response
    address = data.get("address", {})
    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("county")
        or address.get("state")
        or ""
    )
    if city:
        logger.info(
            "Geographic midpoint: %s → %s → (%s) = %.4f,%.4f",
            origin[:40], destination[:40], city, mid_lat, mid_lon,
        )
        return city

    logger.info("Geographic midpoint: no city found at (%.4f, %.4f)", mid_lat, mid_lon)
    return None


def _geocode_nominatim(addr: str) -> tuple[float, float] | None:
    """Geocode a location name to (lat, lon) using Nominatim.

    Free, global coverage, 1 req/s rate limit.  Returns None on failure.
    """
    import json
    import urllib.request

    params = urllib.parse.urlencode({"q": addr, "format": "json", "limit": 1})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Plan-It/0.3"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data:
                return (float(data[0]["lat"]), float(data[0]["lon"]))
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Drive helpers
# ---------------------------------------------------------------------------


def _is_long_drive(driving_time: str) -> bool:
    m = re.search(r'(\d+)', driving_time)
    if m:
        num = int(m.group(1))
        if "hour" in driving_time.lower():
            return num >= 2
        if "min" in driving_time.lower():
            return num >= 120
    return False


def _estimate_total_drive(route: list[dict]) -> float:
    total_min = 0
    for leg in route:
        step = leg.get("step", "")
        h_match = re.search(r'(\d+)\s*hour', step)
        m_match = re.search(r'(\d+)\s*min', step)
        if h_match:
            total_min += int(h_match.group(1)) * 60
        if m_match:
            total_min += int(m_match.group(1))
    return total_min / 60.0


def _user_mentioned_flying(user_input: str) -> bool:
    """Detect if the user mentioned air travel, ferries, boats, or trains."""
    text_lower = user_input.lower()
    transit_keywords = [
        "fly ", "flight", "flying", "airport", "plane", "airline",
        "ferry", "boat ", "cruise", "sail", "water taxi",
        "train", "amtrak", "rail", "subway", "metro",
    ]
    return any(kw in text_lower for kw in transit_keywords)


def _route_looks_undriveable(route: list[dict]) -> bool:
    """Return True if the route text suggests an undriveable distance.

    Looks for phrases like 'too far to drive', international mentions,
    or missing numeric drive-time estimates (which implies the route
    couldn't be calculated — common for cross-continent trips).
    """
    combined = " ".join(leg.get("step", "") for leg in route).lower()
    undriveable_signals = [
        "too far", "overseas", "international", "fly ",
        "head to", "get directions",  # generic placeholder when routing fails
    ]
    # If the route has no numeric time AND no miles mentioned, it's a
    # placeholder — likely undriveable.
    has_time = bool(re.search(r'\d+\s*(hour|min)', combined))
    has_miles = bool(re.search(r'\d+\s*mi', combined))
    if not has_time and not has_miles:
        return True
    return any(signal in combined for signal in undriveable_signals)


# Known international city/country names that indicate cross-border travel
_INTERNATIONAL_SIGNALS = {
    "brazil", "mexico", "canada", "france", "uk", "england", "germany",
    "japan", "china", "australia", "italy", "spain", "portugal", "india",
    "south korea", "singapore", "dubai", "uae", "netherlands", "switzerland",
    "saõ paulo", "rio", "buenos aires", "santiago", "bogota", "lima",
    "london", "paris", "tokyo", "berlin", "rome", "madrid", "sydney",
    "toronto", "vancouver", "montreal", "amsterdam", "brussels",
    "copenhagen", "stockholm", "oslo", "helsinki", "dublin",
    "Lisbon", "barcelona", "milan", "venice", "prague", "vienna",
    "budapest", "warsaw", "athens", "istanbul", "moscow",
    "seoul", "bangkok", "hanoi", "kuala lumpur", "jakarta",
    "mumbai", "delhi", "cairo", "cape town", "nairobi",
    "auckland", "wellington",
}


def _looks_international(origin: str, destination: str) -> bool:
    """Return True if origin/destination suggest international travel.

    Checks for known non-US city/country names in either location.
    This is a heuristic — not authoritative — but catches the common
    case of cross-border trips that need passport/currency tips.
    """
    combined = f"{origin} {destination}".lower()
    return any(signal in combined for signal in _INTERNATIONAL_SIGNALS)
# Schedule construction
# ---------------------------------------------------------------------------


def _build_schedule(
    intent: dict[str, str],
    venue: dict,
    route: list[dict],
    is_multiday: bool = False,
    starting_location: str | None = None,
    departure_time: str | None = None,
) -> list[dict]:
    """Build a full day schedule with support for multi-day trips.

    For multi-day trips, the schedule includes:
      - Day 1: Full venue itinerary with lunch restaurant
      - Day 2: Check-out, breakfast, lunch, and return drive home
    """
    if departure_time:
        dep_time_str = departure_time
    else:
        # No user-provided departure time — leave schedule times empty or use defaults
        dep_time_str = "08:00 AM"
    dep_hour, dep_min = _parse_time(dep_time_str)

    venue_type = venue.get("venue_type", "general")
    attractions = venue.get("top_attractions", [f"Explore {intent['venue']}"])
    tips = venue.get("crowd_tips", [])

    # Determine how many attractions to schedule based on venue type
    max_attractions = _max_attraction_count(venue_type, len(attractions))

    schedule: list[dict] = []

    drive_min = _estimate_drive_minutes(route[0].get("step", "")) if route else 0
    # Account for every rest / breakfast / coffee stop in the route.
    # Long drives insert mandatory stops every ~4 hours; each adds
    # approximately the duration stated in its step text (default 20 min).
    for leg in route[1:]:
        step_lower = leg.get("step", "").lower()
        if any(kw in step_lower for kw in ("rest stop", "breakfast", "coffee", "brunch", "lunch", "dinner")):
            time_match = re.search(r'~(\d+)\s*min', step_lower)
            stop_min = int(time_match.group(1)) if time_match else 20
            drive_min += stop_min

    arrival_h = dep_hour
    arrival_m = dep_min + drive_min
    while arrival_m >= 60:
        arrival_m -= 60
        arrival_h += 1

    arrival_time = _fmt_time(arrival_h, arrival_m)
    day_start_hour = _infer_venue_open_hour(venue_type, venue)

    # =========================================================================
    # Day 1 — Arrival and venue itinerary
    # =========================================================================

    schedule.append({
        "time": arrival_time,
        "action": f"Arrive at {intent['venue']} — get your bearings and check the map",
        "priority": "high",
        "walking_time_min": 0,
        "wait_time_min": None,
        "restaurant": None,
        "meal_timing_note": None,
        "reminder_min": None,
        "walking_map_url": None,
        "backup_plan": None,
    })

    if arrival_h < day_start_hour:
        schedule.append({
            "time": arrival_time,
            "action": f"Grab coffee and a light breakfast near the entrance — opens at {_fmt_time(day_start_hour, 0)}",
            "priority": "medium",
            "walking_time_min": 2,
            "wait_time_min": None,
            "restaurant": "Nearby café or coffee shop",
            "meal_timing_note": None,
            "reminder_min": None,
            "walking_map_url": None,
            "backup_plan": None,
        })

    current_h = max(arrival_h, day_start_hour)
    current_m = 0 if current_h > arrival_h else arrival_m

    day_end_hour = _infer_venue_close_hour(venue_type, venue)

    # If arrival is after closing time, cap Day 1 and push attractions to
    # "tomorrow" so events aren't scheduled at 3 AM when venues are closed.
    attractions_tomorrow: list[str] = []
    if current_h >= day_end_hour:
        attractions_tomorrow = list(attractions[:max_attractions])
        max_attractions = 0  # skip attraction loop for today

    for i, attraction in enumerate(attractions[:max_attractions]):
        # Stop scheduling if we've reached closing time — push remaining
        # attractions to tomorrow so they appear during actual operating hours.
        if current_h >= day_end_hour:
            attractions_tomorrow = list(attractions[i:max_attractions])
            break

        walk = random.randint(3, 12) if i > 0 else 0
        # Wait times ramp up as the day progresses
        if current_h < 10:
            wait = random.randint(5, 15)
        elif current_h < 12:
            wait = random.randint(10, 25)
        else:
            wait = random.randint(15, 45)

        current_m += walk + wait
        while current_m >= 60:
            current_m -= 60
            current_h += 1

        # Priority tiering: first 3 are high, next 4 medium, rest low
        if i < 3:
            priority = "high"
        elif i < 7:
            priority = "medium"
        else:
            priority = "low"

        is_lunch_slot = current_h in (11, 12, 13)
        action_text = f"Visit {attraction}"
        if tips and i == 0:
            action_text += f" — tip: {tips[0][:80]}"

        maps_url = None
        if i > 0 and i - 1 < len(attractions):
            prev = urllib.parse.quote(attractions[i - 1].split(" — ")[0], safe="")
            curr = urllib.parse.quote(attraction.split(" — ")[0], safe="")
            maps_url = f"https://www.google.com/maps/dir/?api=1&origin={prev}&destination={curr}&travelmode=walking"

        schedule.append({
            "time": _fmt_time(current_h, current_m),
            "action": action_text,
            "priority": priority,
            "walking_time_min": walk,
            "wait_time_min": wait,
            "restaurant": "Restaurant recommendation TBD" if is_lunch_slot else None,
            "meal_timing_note": "Beat the lunch crowd — dine early or after 1 PM" if is_lunch_slot else None,
            "reminder_min": None,
            "walking_map_url": maps_url,
            "backup_plan": f"If {attraction.split(' — ')[0]} is closed or too crowded, explore nearby exhibits instead",
        })

    # =========================================================================
    # Day 2 — Return trip (multi-day only)
    # =========================================================================
    if is_multiday and starting_location:
        # Evening hotel check-in on Day 1
        dest_name = intent["venue"]
        if intent.get("location"):
            dest_name = f"{intent['venue']} {intent['location']}"
        origin = starting_location

        schedule.append({
            "time": _fmt_time(min(current_h + 1, 21), 0),
            "action": f"Check into hotel near {dest_name} — unwind and refresh",
            "priority": "high",
            "walking_time_min": 0,
            "wait_time_min": None,
            "restaurant": None,
            "meal_timing_note": None,
            "reminder_min": None,
            "walking_map_url": None,
            "backup_plan": None,
        })

        # Day 2 header
        schedule.append({
            "time": "08:00 AM +1",
            "action": "Day 2 — Check out of hotel. Grab breakfast nearby before the return drive.",
            "priority": "high",
            "walking_time_min": 0,
            "wait_time_min": None,
            "restaurant": "Restaurant recommendation TBD",
            "meal_timing_note": "Start the drive home with a full meal — look for diners or breakfast spots near the hotel",
            "reminder_min": None,
            "walking_map_url": None,
            "backup_plan": None,
        })

        midpoint = _infer_midpoint(dest_name, origin)
        schedule.append({
            "time": "12:00 PM +1",
            "action": f"Day 2 — Lunch stop near {midpoint} — stretch your legs and refuel for the rest of the drive",
            "priority": "medium",
            "walking_time_min": 0,
            "wait_time_min": None,
            "restaurant": "Restaurant recommendation TBD",
            "meal_timing_note": f"Midpoint of {dest_name} → {origin} — good time to take a break",
            "reminder_min": None,
            "walking_map_url": f'https://www.google.com/maps/search/restaurants+near+{_maps_search_location(midpoint, dest_name, origin)}',
            "backup_plan": f"Grab fast food or pack snacks for the road if pressed for time",
        })

        # Return drive leg
        ret_transit = search.search_transit(dest_name, origin)
        ret_drive = (ret_transit.get("driving_time", "") or "").strip()
        ret_action = f"Day 2 — Drive back to {origin}"
        if ret_drive and ret_drive[0].isdigit():
            ret_action += f" — approximately {ret_drive}"
        else:
            ret_action += " — open map for return directions"
        schedule.append({
            "time": "01:30 PM +1",
            "action": ret_action,
            "priority": "medium",
            "walking_time_min": 0,
            "wait_time_min": None,
            "restaurant": None,
            "meal_timing_note": None,
            "reminder_min": None,
            "walking_map_url": ret_transit.get(
                "maps_url",
                f'https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(origin, safe="")}',
            ),
            "backup_plan": None,
        })

        schedule.append({
            "time": "04:30 PM +1",
            "action": f"Day 2 — Arrive home in {origin} — trip complete! Use the app anytime for your next adventure.",
            "priority": "high",
            "walking_time_min": 0,
            "wait_time_min": None,
            "restaurant": None,
            "meal_timing_note": None,
            "reminder_min": None,
            "walking_map_url": None,
            "backup_plan": None,
        })

        # Add return drive to route for completeness
        dest_enc = urllib.parse.quote(origin, safe="")
        ret_step = f"Return drive: {dest_name} → {origin}"
        if ret_drive and ret_drive[0].isdigit():
            ret_step += f" — approximately {ret_drive}"
        else:
            ret_step += " — open map for return directions"
        route.append({
            "step": ret_step,
            "maps_url": f'https://www.google.com/maps/dir/?api=1&destination={dest_enc}',
        })

    return schedule


def _max_attraction_count(venue_type: str, available: int) -> int:
    """How many attractions to schedule based on venue type."""
    defaults = {
        "theme_park": 12,
        "museum": 8,
        "zoo": 8,
        "national_park": 10,
        "city_tour": 8,
        "festival": 6,
    }
    cap = defaults.get(venue_type, 6)
    return min(cap, available)


def _inject_restaurants(
    schedule: list[dict],
    restaurants: list[dict[str, str]],
    preferences: str | None = None,
) -> list[dict]:
    if not restaurants:
        return schedule

    for item in schedule:
        if item.get("restaurant") and "TBD" in str(item.get("restaurant", "")):
            if restaurants:
                r = restaurants.pop(0)
                item["restaurant"] = f"{r['name']} — {r['cuisine']}, {r['price_range']}, {r['location']}"
                if preferences:
                    item["meal_timing_note"] = (item.get("meal_timing_note") or "") + f" (filtered by: {preferences})"

    for item in schedule:
        if item.get("restaurant") and "TBD" not in str(item.get("restaurant", "")) and len(restaurants) > 1:
            alt = restaurants[1]
            item["backup_plan"] = f"Alternative: {alt['name']} — {alt['cuisine']}, {alt['price_range']}"

    return schedule


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------


def _pick_departure_time(intent: dict[str, str], venue: dict) -> str:
    venue_type = venue.get("venue_type", "general")
    hour = 7
    if venue_type in ("museum", "zoo", "general"):
        hour = 8
    if venue_type == "national_park":
        hour = 6
    if venue_type == "festival":
        hour = 10
    time_of_day = intent.get("time_of_day", "morning")
    if time_of_day == "afternoon":
        hour = 12
    if time_of_day == "evening":
        hour = 16
    return _fmt_time(hour, 0)


def _infer_venue_open_hour(venue_type: str, venue: dict) -> int:
    hours_text = venue.get("hours", "")
    m = re.search(r'(\d{1,2})\s*(?::\d{2})?\s*(?:AM|am)', hours_text)
    if m:
        return int(m.group(1))
    defaults = {
        "theme_park": 7,
        "museum": 9,
        "zoo": 9,
        "national_park": 6,
        "festival": 10,
        "city_tour": 8,
    }
    return defaults.get(venue_type, 9)


def _infer_venue_close_hour(venue_type: str, venue: dict) -> int:
    """Return the 24-hour closing hour for a venue type."""
    hours_text = venue.get("hours", "")
    m = re.search(r'(\d{1,2})\s*(?::\d{2})?\s*(?:PM|pm)', hours_text)
    if m:
        h = int(m.group(1))
        return h + 12 if h < 12 else h
    defaults = {
        "theme_park": 22,
        "museum": 17,
        "zoo": 17,
        "national_park": 20,
        "festival": 22,
        "city_tour": 21,
    }
    return defaults.get(venue_type, 21)


def _estimate_drive_minutes(step: str) -> int:
    h_match = re.search(r'(\d+)\s*hour', step)
    m_match = re.search(r'(\d+)\s*min', step)
    total = 0
    if h_match:
        total += int(h_match.group(1)) * 60
    if m_match:
        total += int(m_match.group(1))
    return total if total > 0 else 0


def _check_traffic_warning(step: str) -> str | None:
    step_lower = step.lower()
    if "i-4" in step_lower or "orlando" in step_lower:
        return "⚠ Traffic on I-4 can add 30+ minutes during peak hours — consider an early start"
    if "i-95" in step_lower or "miami" in step_lower or "jacksonville" in step_lower:
        return "⚠ I-95 congestion common 7-9 AM and 4-7 PM"
    if "atlanta" in step_lower or "i-75" in step_lower or "i-85" in step_lower:
        return "⚠ Atlanta metro traffic is heavy — allow extra 30-45 min during rush hours"
    if "tampa" in step_lower or "i-275" in step_lower:
        return "⚠ Tampa Bay area traffic can be heavy near bridges and I-275 during peak hours"
    return None


def _default_flights(origin: str, destination: str) -> list[dict[str, str]]:
    return [
        {
            "airline": "Delta",
            "route": f"{origin} → {destination}",
            "estimated_price": "$250-400 round trip",
            "flight_time": "~3-4 hours",
            "booking_url": "https://www.kayak.com/flights",
        },
        {
            "airline": "United",
            "route": f"{origin} → {destination}",
            "estimated_price": "$230-380 round trip",
            "flight_time": "~3-4 hours",
            "booking_url": "https://www.united.com",
        },
    ]


def _default_parking(origin: str) -> list[dict[str, str]]:
    return [
        {
            "name": f"Long-term parking near {origin}",
            "type": "Economy Lot",
            "daily_rate": "$8-12/day",
            "shuttle": "Free shuttle to terminal every 10-15 min",
            "location": f"On-site — {origin}",
            "booking_url": "https://www.wallypark.com",
        },
    ]