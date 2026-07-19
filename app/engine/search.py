"""Multi-backend search engine — zero API keys required.

Performs web research for venues, restaurants, transit, hotels, and
alerts.  Primary backends:

* **DuckDuckGo** (via ``ddgs``) — default, no API key, rate-limited at ~1 QPS
* **SearxNG** (via public or self-hosted instance) — privacy-respecting
  metasearch engine, JSON API, no API key

Both backends are free and require zero authentication.  The active
backend is controlled by the ``SEARCH_BACKEND`` env var (``ddg``,
``searxng``, or ``auto``); ``auto`` tries DuckDuckGo first and
fails over to SearxNG on error or empty results.

Dependencies:
    ddgs>=9.0    (MIT licensed, no API key — DuckDuckGo backend)
    urllib       (stdlib — SearxNG backend)
"""

from __future__ import annotations

import json
import logging
import time
import urllib.parse
import urllib.request
from functools import lru_cache
from typing import Any

from app.config import get_settings
from app.engine import db

logger = logging.getLogger("plan-it.search")

# ---------------------------------------------------------------------------
# Rate limiting — shared across backends for fair use.
# ---------------------------------------------------------------------------
_MIN_INTERVAL_S = 1.2  # seconds between queries
_last_query: float = 0.0


def _rate_wait() -> None:
    """Block until the minimum interval since the last query has elapsed."""
    global _last_query
    elapsed = time.monotonic() - _last_query
    if elapsed < _MIN_INTERVAL_S:
        time.sleep(_MIN_INTERVAL_S - elapsed)
    _last_query = time.monotonic()


# ---------------------------------------------------------------------------
# Backend: DuckDuckGo (lazy import — ddgs is heavy)
# ---------------------------------------------------------------------------
_ddgs: Any = None


def _ddg() -> Any:
    global _ddgs
    if _ddgs is None:
        from ddgs import DDGS

        _ddgs = DDGS()
    return _ddgs


def _search_ddg(query: str, max_results: int = 8) -> list[dict[str, str]]:
    """Run a DuckDuckGo text search via the ``ddgs`` library.

    Returns a list of dicts with keys ``title``, ``href``, ``body``.
    Returns an empty list on failure (never raises).
    """
    _rate_wait()
    try:
        results = list(_ddg().text(query, max_results=max_results))
        logger.info("ddg search: %r → %d results", query[:80], len(results))
        return results
    except Exception as exc:
        logger.warning("DuckDuckGo search failed for %r: %s", query[:80], exc)
        return []


# ---------------------------------------------------------------------------
# Backend: SearxNG (public or self-hosted instance, JSON API)
# ---------------------------------------------------------------------------

_SEARXNG_CATEGORIES = "general,news"  # SearxNG category filter for web results


def _search_searxng(query: str, max_results: int = 8) -> list[dict[str, str]]:
    """Run a search against a SearxNG instance.

    Uses the public ``https://searx.be`` instance by default, overridable
    via the ``SEARXNG_INSTANCE`` environment variable.

    Returns a list of dicts with keys ``title``, ``href``, ``body``.
    Returns an empty list on failure (never raises).
    """
    settings = get_settings()
    instance = settings.SEARXNG_INSTANCE.rstrip("/")
    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "categories": _SEARXNG_CATEGORIES,
        "pageno": 1,
    })
    url = f"{instance}/search?{params}"

    _rate_wait()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Plan-It/0.3"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception as exc:
        logger.warning("SearxNG search failed for %r: %s", query[:80], exc)
        return []

    results: list[dict[str, str]] = []
    for entry in data.get("results", [])[:max_results]:
        results.append({
            "title": entry.get("title", ""),
            "href": entry.get("url", ""),
            "body": entry.get("content", ""),
        })

    logger.info("searxng search: %r → %d results", query[:80], len(results))
    return results


# ---------------------------------------------------------------------------
# Public API — unified search with configurable backend + failover
# ---------------------------------------------------------------------------

def search_web(query: str, max_results: int = 8) -> list[dict[str, str]]:
    """Run a web search and return a list of result dicts.

    Each dict has keys: ``title``, ``href``, ``body``.

    The active backend is determined by the ``SEARCH_BACKEND`` env var:
    - ``ddg`` — DuckDuckGo only
    - ``searxng`` — SearxNG only
    - ``auto`` (default) — DDG first, fails over to SearxNG on error/empty

    Args:
        query: The search query string.
        max_results: Maximum number of results to return.

    Returns:
        List of dicts, empty list if all backends fail.
    """
    settings = get_settings()
    backend = settings.SEARCH_BACKEND.lower()

    if backend == "searxng":
        return _search_searxng(query, max_results)

    if backend == "ddg":
        return _search_ddg(query, max_results)

    # "auto" — try DDG first, fall back to SearxNG
    results = _search_ddg(query, max_results)
    if results:
        return results

    logger.info("DDG returned 0 results — failing over to SearxNG for %r", query[:80])
    return _search_searxng(query, max_results)


@lru_cache(maxsize=200)
def search_venue_info(venue_name: str, location: str = "") -> dict[str, Any]:
    """Research a specific venue and return structured info.

    Returns a dict with keys:
        venue_type: str       — theme_park, museum, zoo, national_park, city_tour, general
        description: str      — summary paragraph
        hours: str            — typical operating hours
        top_attractions: list[str] — 3-5 must-see attractions
        crowd_tips: list[str]      — crowd-avoidance strategies
        parking_info: str     — parking guidance
        alerts: list[str]            — known closures, construction, etc.
    """
    q = f"{venue_name} {location} visitor guide hours tickets top attractions"
    results = search_web(q, max_results=12)

    # Extract venue type
    venue_type = _classify_venue(venue_name, " ".join(r.get("body", "") for r in results))

    # Extract top attractions from results
    attractions: list[str] = []
    seen_attractions: set[str] = set()
    for r in results:
        body = r.get("body", "")
        for phrase in _extract_attraction_names(body):
            if phrase not in seen_attractions:
                seen_attractions.add(phrase)
                attractions.append(phrase)
        if len(attractions) >= 5:
            break

    # Prefer curated attraction knowledge base when available, falling back
    # to web-extracted names only when no curated entries exist for this venue.
    curated = _lookup_curated_attractions(venue_name, location)
    if curated:
        # Curated entries are authoritative — use them instead of regex-extracted noise
        attractions = list(curated)
        seen_attractions = set(c.lower() for c in curated)
    elif len(attractions) < 3:
        # No curated data — keep web results but only if we got enough
        pass

    # Build description from first few results
    description = " ".join(r.get("body", "") for r in results[:3])[:600]

    # Search specifically for hours and tips
    hours_results = search_web(f"{venue_name} operating hours opening time", max_results=3)
    hours = "Typically 9:00 AM – 5:00 PM"
    for r in hours_results:
        body = r.get("body", "")
        if "am" in body.lower() or "pm" in body.lower():
            hours = body[:200]
            break

    tips_results = search_web(f"{venue_name} tips best time to visit avoid crowds", max_results=3)
    crowd_tips: list[str] = []
    for r in tips_results:
        body = r.get("body", "")
        tip = _extract_crowd_tip(body)
        if tip and len(crowd_tips) < 4:
            crowd_tips.append(tip)

    parking_results = search_web(f"{venue_name} parking where to park", max_results=3)
    parking = "Parking available on-site"
    for r in parking_results:
        body = r.get("body", "")
        if "park" in body.lower():
            parking = body[:200]

    return {
        "venue_type": venue_type,
        "description": description,
        "hours": hours,
        "top_attractions": attractions if attractions else [f"Main entrance — {venue_name}"],
        "crowd_tips": crowd_tips if crowd_tips else ["Arrive 30 minutes before opening"],
        "parking_info": parking,
        "alerts": [],
    }


@lru_cache(maxsize=200)
def search_restaurants(
    venue_area: str,
    preferences: str = "",
    count: int = 4,
) -> list[dict[str, str]]:
    """Search for real restaurants near a venue area.

    Args:
        venue_area: Area name (e.g. "near Kennedy Space Center", "downtown Nashville").
        preferences: Dietary/cuisine preferences string.
        count: Number of restaurants to return.

    Returns:
        List of dicts with: name, cuisine, price_range, location, notes.
    """
    prefs = f" {preferences}" if preferences else ""
    q = f"best restaurants {venue_area}{prefs} top rated"
    results = search_web(q, max_results=count + 4)

    restaurants: list[dict[str, str]] = []
    seen: set[str] = set()

    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")

        # Try to extract a restaurant name from title/body
        name = _extract_restaurant_name(title, body)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())

        cuisine = _infer_cuisine(body)
        price = _infer_price(body)

        restaurants.append(
            {
                "name": name,
                "cuisine": cuisine,
                "price_range": price,
                "location": venue_area,
                "notes": body[:200],
            }
        )
        if len(restaurants) >= count:
            break

    return restaurants


@lru_cache(maxsize=100)
def search_hotels(
    area: str,
    count: int = 3,
) -> list[dict[str, Any]]:
    """Search for 3+ star hotels in an area."""
    q = f"best hotels {area} 3 star 4 star amenities"
    results = search_web(q, max_results=count + 3)

    hotels: list[dict[str, Any]] = []
    seen: set[str] = set()

    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")

        name = _extract_hotel_name(title, body)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())

        stars = 3
        if "4 star" in (title + body).lower() or "four star" in (title + body).lower():
            stars = 4
        if "5 star" in (title + body).lower() or "five star" in (title + body).lower():
            stars = 5

        hotels.append(
            {
                "name": name,
                "star_rating": stars,
                "price_range": _infer_price(body),
                "location": area,
                "highlights": _extract_amenities(body),
                "booking_url": "https://www.booking.com",
            }
        )
        if len(hotels) >= count:
            break

    # If search returned garbage, fall back to curated hotel list for this city
    if len(hotels) < count:
        area_lower = area.lower()
        for city_key, fallback_hotels in _HOTEL_FALLBACKS.items():
            if city_key in area_lower:
                for fb in fallback_hotels:
                    if fb["name"].lower() not in seen:
                        seen.add(fb["name"].lower())
                        hotels.append(dict(fb))
                        if len(hotels) >= count:
                            break
                break

    return hotels


def search_transit(origin: str, destination: str) -> dict[str, str]:
    """Get transit/driving info between two points.

    Uses Nominatim geocoding + OSRM real road-network routing
    (both free, no API keys). No DuckDuckGo fallback — drive times
    are computed from actual route geometry only.

    Returns:
        Dict with: driving_time, transit_tip, maps_url.
    """
    import urllib.parse

    osrm_result = _osrm_transit(origin, destination)
    if osrm_result:
        return osrm_result

    # Routing failed entirely — return a placeholder with a
    # Google Maps link so the user can still get directions manually.
    maps_url = f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(origin)}&destination={urllib.parse.quote(destination)}"
    logger.warning("All transit methods failed for %s → %s", origin[:40], destination[:40])
    return {
        "driving_time": "",
        "transit_tip": "",
        "maps_url": maps_url,
    }


# ---------------------------------------------------------------------------
# US state name ↔ code mapping (supports both "FL" and "Florida")
# ---------------------------------------------------------------------------
from app.engine.states import (  # noqa: E402  — shared source of truth
    CODE_TO_NAME,
    STATE_PATTERN_2LETTER,
    US_STATE_NAMES,
    resolve_state_code,
)

# Backward-compatible aliases for internal use
_US_STATE_NAMES = US_STATE_NAMES
_CODE_TO_NAME = CODE_TO_NAME
_STATE_PATTERN_2LETTER = STATE_PATTERN_2LETTER
_resolve_state_code = resolve_state_code


def _extract_state(text: str) -> tuple[str, str]:
    """Extract a US state from text, returning (code, remainder_without_state).

    Supports both 2-letter codes ("FL") and spelled-out names ("Florida").
    Always returns the 2-letter code. Returns ("", original text) on no match.
    """
    import re

    # 1. Try spelled-out state names first (longest match wins to avoid "New York" being "New")
    best_len = 0
    best_code = ""
    text_lower = text.lower()
    for name, code in sorted(_US_STATE_NAMES.items(), key=lambda x: -len(x[0])):
        if name in text_lower and len(name) > best_len:
            best_len = len(name)
            best_code = code

    if best_code:
        for full_name, code in _US_STATE_NAMES.items():
            if code == best_code and len(full_name) == best_len:
                remainder = re.sub(
                    r'\b' + re.escape(full_name) + r'\b', '', text, count=1, flags=re.IGNORECASE,
                )
                return (best_code, remainder.strip())
        return (best_code, text)

    # 2. Fall back to 2-letter abbreviation
    state_match = re.search(_STATE_PATTERN_2LETTER, text)
    if state_match:
        code = state_match.group(1).upper()
        remainder = re.sub(
            r'\b' + state_match.group(1) + r'\b', '', text, count=1, flags=re.IGNORECASE,
        )
        return (code, remainder.strip())

    return ("", text)


def _geocode_census(addr: str) -> tuple[float, float] | None:
    """Geocode a US address using the Census Bureau's free geocoder.

    Handles structured US addresses (street, city, state, zip) that
    Nominatim often fails on. No API key, no rate limit.

    Returns (lat, lon) or None.
    """
    import re
    import json
    import urllib.request
    import urllib.parse

    # Parse address components from the input string.
    # Only handles comma-separated US addresses ("123 Main St, City, ST 12345").
    # Unstructured addresses (no commas) fall through to Nominatim which
    # handles free-form geocoding natively.
    parts = [p.strip() for p in addr.split(",")]
    if len(parts) < 2:
        return None

    street = parts[0]
    # Extract zip code from the last part
    zip_match = re.search(r'\b(\d{5}(?:-\d{4})?)\b', parts[-1])
    zip_code = zip_match.group(1) if zip_match else ""
    # Census geocoder requires either a street address or a zip code.
    # If we have neither, bail early and let Nominatim handle it.
    has_street_number = bool(re.search(r'\d', parts[0]))
    if not has_street_number and not zip_code:
        return None
    # Extract state — supports both 2-letter codes (FL) and full names (Florida)
    state, remainder_state = _extract_state(parts[-1])
    # City is the second-to-last part if we have 3+ parts, stripping zip/state
    if len(parts) >= 3:
        city = parts[-2].strip()
    elif len(parts) == 2 and state:
        # Two-part address: "City, State" or "City, State Zip"
        # If parts[0] looks like a street address (contains digits), treat it as street;
        # otherwise treat it as the city (e.g. "Jacksonville, Florida").
        if re.search(r'\d', parts[0]):
            street_part = parts[0]
            # Derive city from the state-part remainder (after stripping state + zip)
            remainder = re.sub(r'\b\d{5}(?:-\d{4})?\b', '', parts[1])
            remainder = re.sub(r'\b[A-Za-z]{2}\b', '', remainder)
            for full_name in _US_STATE_NAMES:
                remainder = re.sub(r'\b' + re.escape(full_name) + r'\b', '', remainder, flags=re.IGNORECASE)
            city = remainder.strip().rstrip(",").strip()
        else:
            # No street number — parts[0] is the city
            city = parts[0].strip()
            street = ""  # city-level geocoding; Census handles empty street
    else:
        city = ""

    # Require at minimum city + state. Street and zip are optional for
    # city-level geocoding (the Census API handles empty street/zip).
    if not city or not state:
        return None
    has_street = bool(re.search(r'\d', street))
    if has_street and not zip_code:
        # Street-level geocoding needs a zip for accuracy
        return None

    params = urllib.parse.urlencode({
        "street": street,
        "city": city,
        "state": state,
        "zip": zip_code,
        "benchmark": "Public_AR_Current",
        "format": "json",
    })
    url = f"https://geocoding.geo.census.gov/geocoder/locations/address?{params}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data.get("result", {}).get("addressMatches"):
                coords = data["result"]["addressMatches"][0]["coordinates"]
                logger.info("Census geocoded: %r → (%f, %f)", addr[:60], coords["y"], coords["x"])
                return (coords["y"], coords["x"])
            return None
    except Exception:
        return None


def _geocode_nominatim(addr: str) -> tuple[float, float] | None:
    """Geocode an address using Nominatim (OpenStreetMap).

    Global coverage, free, 1 req/s rate limit.

    Returns (lat, lon) or None.
    """
    import json
    import time
    import urllib.request
    import urllib.parse

    params = urllib.parse.urlencode({"q": addr, "format": "json", "limit": 1})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Plan-It/0.3"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data:
                logger.info("Nominatim geocoded: %r → (%s, %s)", addr[:60], data[0]["lat"], data[0]["lon"])
                return (float(data[0]["lat"]), float(data[0]["lon"]))
            return None
    except Exception as exc:
        logger.warning("Nominatim failed for %r: %s", addr[:60], exc)
        return None


def _osrm_transit(origin: str, destination: str) -> dict[str, str] | None:
    """Calculate real-world drive time using OpenStreetMap routing.

    Uses Nominatim (free geocoding) to convert addresses to coordinates,
    then the OSRM public routing API to calculate actual drive duration
    on the real road network. No API keys, no rate limits beyond fair use.

    Returns None when geocoding or routing fails.
    """
    import urllib.request
    import urllib.parse
    import json
    import time

    # ── Step 1: Geocode both addresses to lat/lon ──────────────────────
    # Uses a two-layer strategy:
    #   a) US Census geocoder (best for structured US addresses, no rate limit)
    #   b) Nominatim (global fallback, 1 req/s rate limit)
    coords: list[tuple[float, float]] = []
    for addr in (origin, destination):
        coord = _geocode_census(addr)
        if coord:
            coords.append(coord)
            continue
        time.sleep(1.2)  # Nominatim rate limit: 1 req/s
        coord = _geocode_nominatim(addr)
        if coord:
            coords.append(coord)
            continue
        logger.warning("All geocoders failed for %r", addr[:60])
        return None

    lat1, lon1 = coords[0]
    lat2, lon2 = coords[1]

    # ── Step 2: Real routing via OSRM public API ───────────────────────
    # OSRM uses lon,lat order in the URL
    route_url = f"https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    try:
        req = urllib.request.Request(route_url, headers={"User-Agent": "Plan-It/0.3"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            if data.get("code") != "Ok" or not data.get("routes"):
                logger.warning("OSRM routing failed for (%f,%f)→(%f,%f)", lat1, lon1, lat2, lon2)
                return None
            route = data["routes"][0]
            duration_seconds = route["legs"][0]["duration"]
            distance_meters = route["legs"][0]["distance"]
    except Exception as exc:
        logger.warning("OSRM routing request failed: %s", exc)
        return None

    # ── Step 3: Format as human-readable drive time ─────────────────────
    minutes = int(duration_seconds / 60)
    miles = int(distance_meters / 1609.34)

    if minutes < 60:
        driving_time = f"{minutes} minutes"
    else:
        hours = minutes // 60
        remaining_mins = minutes % 60
        if remaining_mins == 0:
            driving_time = f"{hours} hours"
        else:
            driving_time = f"{hours} hours {remaining_mins} minutes"

    maps_url = f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(origin)}&destination={urllib.parse.quote(destination)}"

    result = {
        "driving_time": driving_time,
        "transit_tip": f"{driving_time} ({miles} mi) via fastest route",
        "maps_url": maps_url,
    }
    logger.info("OSRM route: %s → %s: %s (%d mi)", origin[:40], destination[:40], driving_time, miles)
    return result


def search_rental_cars(location: str) -> list[dict[str, str]]:
    """Return generic rental car recommendations for a location."""
    return [
        {
            "company": "Enterprise Rent-A-Car",
            "car_type": "Mid-size Sedan",
            "estimated_daily_rate": "$45-65/day",
            "pickup_location": f"{location} — local branch",
            "booking_url": "https://www.enterprise.com",
        },
        {
            "company": "Hertz",
            "car_type": "Compact SUV",
            "estimated_daily_rate": "$55-75/day",
            "pickup_location": f"{location} — on-site counter",
            "booking_url": "https://www.hertz.com",
        },
        {
            "company": "Avis",
            "car_type": "Economy",
            "estimated_daily_rate": "$35-55/day",
            "pickup_location": f"{location} — airport terminal",
            "booking_url": "https://www.avis.com",
        },
    ]


def search_ride_shares(origin: str, destination: str) -> list[dict[str, str]]:
    """Return ride share estimates for a route."""
    return [
        {
            "service": "Uber",
            "route": f"{origin} → {destination}",
            "estimated_cost": "$25-40",
            "estimated_time": "20-30 min",
            "app_url": "https://www.uber.com",
        },
        {
            "service": "Lyft",
            "route": f"{origin} → {destination}",
            "estimated_cost": "$22-38",
            "estimated_time": "20-30 min",
            "app_url": "https://www.lyft.com",
        },
    ]


# ---------------------------------------------------------------------------
# Private helpers — text extraction from search results
# ---------------------------------------------------------------------------

_VENUE_CLASSIFIERS: list[tuple[str, list[str]]] = [
    ("theme_park", ["theme park", "disney", "universal", "busch gardens", "six flags",
                     "sea world", "seaworld", "legoland", "amusement park", "roller coaster"]),
    ("museum", ["museum", "gallery", "exhibit", "collection", "smithsonian", "louvre",
                "metropolitan museum", "natural history"]),
    ("zoo", ["zoo", "aquarium", "wildlife", "safari", "animal park", "aviary"]),
    ("national_park", ["national park", "state park", "wilderness", "forest", "canyon",
                       "yosemite", "yellowstone", "grand canyon", "zion"]),
    ("festival", ["festival", "fair", "carnival", "music festival", "food festival",
                  "art festival", "county fair"]),
    ("city_tour", ["city tour", "downtown", "walking tour", "sightseeing", "landmark",
                   "historic district", "old town"]),
]

# ---------------------------------------------------------------------------
# Curated attraction knowledge base — ensures every venue has real
# exhibits/rides/attractions even when DuckDuckGo results are sparse.
# Maps normalized venue keys to lists of top attractions.
# ---------------------------------------------------------------------------
_VENUE_ATTRACTIONS: dict[str, list[str]] = {
    # --- Theme Parks ---
    "busch gardens tampa": [
        "Iron Gwazi — world's fastest hybrid coaster, 206 ft drop at 91°",
        "SheiKra — floorless dive coaster with 200 ft vertical drop",
        "Cheetah Hunt — triple-launch coaster through the Serengeti",
        "Montu — inverted coaster with 7 inversions and batwing element",
        "Congo River Rapids — whitewater rafting through jungle scenery",
        "Serengeti Safari — open-truck tour feeding giraffes and zebras",
        "Tigris — skyrocket triple-launch coaster with 150 ft tall inversion",
        "Kumba — classic sit-down coaster with 7 inversions at 60 mph",
        "Stanley Falls Flume — log flume with splashdown finale",
        "Falcon's Fury — 335 ft free-fall drop tower, face-down at 60 mph",
        "Serengeti Express — steam train loop through the park",
        "Pantopia — family thrill zone with Scorpion coaster and shows",
    ],
    "busch gardens williamsburg": [
        "Apollo's Chariot — hypercoaster with 210 ft drop at 73 mph",
        "Griffon — floorless dive coaster with 205 ft 90° drop",
        "Alpengeist — inverted coaster through fake snow and ski village",
        "Verbolten — indoor/outdoor launch coaster through the Black Forest",
        "InvadR — wooden coaster with GCI Millennium Flyer trains",
        "Le Scoot — classic log flume through the French countryside",
        "Loch Ness Monster — interlocking-loop coaster, park icon since 1978",
        "Roman Rapids — river rapids through Roman ruins",
    ],
    "universal studios": [
        "Harry Potter and the Escape from Gringotts — 3D dark ride",
        "Hollywood Rip Ride Rockit — vertical lift coaster, pick your own soundtrack",
        "Transformers: The Ride 3D — motion-based dark ride through the city",
        "Revenge of the Mummy — indoor coaster through cursed tomb",
        "Men in Black: Alien Attack — interactive shooter dark ride",
        "E.T. Adventure — flying bicycle dark ride through the forest",
        "The Simpsons Ride — motion simulator through Krustyland",
        "Race Through New York Starring Jimmy Fallon — 3D simulator",
    ],
    "universal islands of adventure": [
        "Hagrid's Magical Creatures Motorbike Adventure — story coaster",
        "The Incredible Hulk Coaster — launched B&M with 0-40 mph in 2s",
        "Jurassic World VelociCoaster — intense launch coaster, 155 ft top hat",
        "Harry Potter and the Forbidden Journey — KUKA arm dark ride",
        "The Amazing Adventures of Spider-Man — 3D motion-based dark ride",
        "Dudley Do-Right's Ripsaw Falls — splash water flume",
        "Popeye & Bluto's Bilge-Rat Barges — whitewater raft ride",
        "Doctor Doom's Fearfall — twin-launched drop towers",
        "Skull Island: Reign of Kong — trackless expedition dark ride",
    ],
    "magic kingdom": [
        "Space Mountain — indoor coaster in the dark at 28 mph",
        "Seven Dwarfs Mine Train — swinging family coaster through the mines",
        "Big Thunder Mountain Railroad — runaway mine train coaster",
        "Splash Mountain — log flume with 5-story splashdown",
        "Pirates of the Caribbean — classic dark boat ride through pirate raids",
        "Haunted Mansion — omnimover dark ride through 999 haunts",
        "Jungle Cruise — pun-filled boat tour through jungle rivers",
        "TRON Lightcycle Run — launched coaster on a lightcycle grid",
        "Peter Pan's Flight — suspended dark ride over London and Neverland",
    ],
    "epcot": [
        "Guardians of the Galaxy: Cosmic Rewind — reverse-launch spinning coaster",
        "Soarin' Around the World — hang-gliding flight simulator",
        "Test Track — design and ride your own concept vehicle at 65 mph",
        "Frozen Ever After — dark boat ride through Arendelle",
        "Remy's Ratatouille Adventure — trackless 4D dark ride through the kitchen",
        "Spaceship Earth — omnimover journey through communication history inside the geosphere",
        "Mission: SPACE — centrifuge-based mission to Mars or Earth orbit",
        "Living with the Land — boat tour through experimental greenhouses",
    ],
    "disney hollywood studios": [
        "Star Wars: Rise of the Resistance — trackless dark ride with Kylo Ren escape",
        "Slinky Dog Dash — family launch coaster in Toy Story Land",
        "The Twilight Zone Tower of Terror — drop tower through the 5th dimension",
        "Rock 'n' Roller Coaster Starring Aerosmith — launched indoor coaster",
        "Millennium Falcon: Smugglers Run — interactive cockpit simulator",
        "Toy Story Mania! — 4D carnival midway shooter ride",
        "Mickey & Minnie's Runaway Railway — trackless cartoon dark ride",
    ],
    "disney animal kingdom": [
        "Avatar Flight of Passage — banshee-back flight simulator over Pandora",
        "Expedition Everest — coaster through the Forbidden Mountain with Yeti encounter",
        "Kilimanjaro Safaris — open-air safari through the Harambe Wildlife Reserve",
        "DINOSAUR — time-traveling EMV ride to rescue an Iguanodon",
        "Kali River Rapids — river raft ride with a conservation theme",
        "Na'vi River Journey — bioluminescent boat ride through Pandora rainforest",
        "It's Tough to Be a Bug! — 4D show inside the Tree of Life",
    ],
    # --- Disneyland Resort (Anaheim, California) ---
    "disneyland": [
        "Star Wars: Rise of the Resistance — trackless dark ride with Kylo Ren escape, Galaxy's Edge",
        "Indiana Jones Adventure — enhanced motion vehicle through the Temple of the Forbidden Eye",
        "Space Mountain — high-speed indoor coaster in the dark with Galactic soundtrack",
        "Pirates of the Caribbean — classic boat ride through pirate raids and Blue Bayou",
        "Haunted Mansion — omnimover through 999 haunts with stretching room pre-show",
        "Big Thunder Mountain Railroad — runaway mine train coaster through the Old West",
        "Matterhorn Bobsleds — dual-track bobsled coaster through the icy mountain peak",
        "Millennium Falcon: Smugglers Run — interactive cockpit simulator in Galaxy's Edge",
        "Peter Pan's Flight — suspended dark ride over London and Neverland",
        "Jungle Cruise — pun-filled boat tour through jungle rivers with comedy skippers",
        "It's a Small World — classic boat ride through international doll-land, Fantasyland",
        "Splash Mountain — log flume with 5-story splashdown finale in Critter Country",
    ],
    "disney california adventure": [
        "Radiator Springs Racers — slot-car style racing coaster through Cars' Ornament Valley",
        "Guardians of the Galaxy — Mission: BREAKOUT! — drop tower with 6 randomized profiles",
        "The Incredicoaster — launched looping coaster through the Incredibles' chase",
        "Soarin' Around the World — hang-gliding flight simulator over global landmarks",
        "Toy Story Midway Mania! — 4D carnival midway shooter game",
        "Grizzly River Run — whitewater raft ride through a California mining mountain",
        "Pixar Pal-A-Round — 160 ft Ferris wheel with swinging and stationary gondolas",
        "Monsters, Inc. Mike & Sulley to the Rescue! — dark ride through Monstropolis",
        "WEB SLINGERS: A Spider-Man Adventure — interactive web-slinging dark ride",
        "Goofy's Sky School — wild mouse coaster along a California postcard route",
        "Luigi's Rollickin' Roadsters — trackless dancing car ride in Radiator Springs",
        "Little Mermaid ~ Ariel's Undersea Adventure — omnimover dark ride under the sea",
    ],
    "seaworld orlando": [
        "Mako — hypercoaster with 200 ft drop at 73 mph, airtime-focused",
        "Manta — face-down flying coaster swooping over lagoons",
        "Kraken — floorless coaster with 7 inversions and underground tunnels",
        "Ice Breaker — 4-launch coaster with beyond-vertical 100° spike",
        "Journey to Atlantis — water coaster / dark ride hybrid",
        "Infinity Falls — world's tallest river rapid drop",
        "Orca Encounter — killer whale presentation with conservation message",
        "Dolphin Days — Atlantic bottlenose dolphin and pilot whale show",
    ],
    "walt disney world": [
        "Magic Kingdom: Space Mountain, Seven Dwarfs Mine Train, Big Thunder Mountain",
        "EPCOT: Guardians of the Galaxy: Cosmic Rewind, Soarin', Test Track",
        "Hollywood Studios: Rise of the Resistance, Tower of Terror, Slinky Dog Dash",
        "Animal Kingdom: Avatar Flight of Passage, Expedition Everest, Kilimanjaro Safaris",
        "Disney Springs — shopping, dining, and entertainment district",
        "Typhoon Lagoon — water park with massive wave pool and slides",
    ],
    "cedar point": [
        "Steel Vengeance — world's tallest hybrid coaster, 205 ft drop at 74 mph",
        "Millennium Force — giga coaster, 310 ft drop at 93 mph",
        "Top Thrill 2 — strata coaster, 420 ft triple-launch top hat",
        "Maverick — beyond-vertical drop LSM launch coaster through canyons",
        "Magnum XL-200 — hypercoaster, 205 ft drop at 72 mph",
        "Valravn — floorless dive coaster, 223 ft drop",
        "Raptor — inverted coaster with 6 inversions",
        "GateKeeper — wing coaster flying over the main entrance",
    ],
    "six flags over georgia": [
        "Goliath — hypercoaster, 200 ft drop at 70 mph",
        "Twisted Cyclone — RMC hybrid coaster, 3 inversions",
        "Batman: The Ride — inverted B&M coaster through Gotham City",
        "Dare Devil Dive — beyond-vertical drop Euro-Fighter",
        "Mind Bender — classic Schwarzkopf looping coaster",
        "Superman: Ultimate Flight — flying coaster",
        "Georgia Scorcher — stand-up coaster through Georgia clay terrain",
        "Monster Mansion — classic dark boat ride with animatronics",
    ],

    # --- Museums ---
    "the louvre": [
        "Mona Lisa by Leonardo da Vinci — Salle des États, Denon Wing",
        "Venus de Milo — Sully Wing, ancient Greek sculpture",
        "Winged Victory of Samothrace — Daru staircase, Hellenistic triumph",
        "The Coronation of Napoleon — Denon Wing, David's monumental canvas",
        "Liberty Leading the People — Delacroix, Denon Wing",
        "The Raft of the Medusa — Géricault, Denon Wing",
        "Code of Hammurabi — Richelieu Wing, Mesopotamian antiquity",
        "Napoleon III Apartments — Richelieu Wing, opulent Second Empire rooms",
        "Great Sphinx of Tanis — Sully Wing, Egyptian antiquities",
        "The Wedding at Cana — Veronese, opposite the Mona Lisa",
    ],
    "the metropolitan museum of art": [
        "Temple of Dendur — Egyptian temple in a glass atrium, Sackler Wing",
        "Washington Crossing the Delaware — Leutze, Gallery 760 American Wing",
        "The Death of Socrates — Jacques-Louis David, European Paintings",
        "Madonna and Child — Duccio, early Italian gold-ground panels",
        "Vermeer Collection — five rare Vermeer paintings in European Masters",
        "Arms and Armor — full suits of European and Japanese armor, Gallery 371",
        "The Astor Chinese Garden Court — Ming-style courtyard garden",
        "Cypresses — Van Gogh, Gallery 822",
        "Modern and Contemporary Art — Pollock, Warhol, Rothko spanning 3 floors",
        "Costume Institute — fashion history from the 15th century to today",
    ],
    "smithsonian": [
        "National Air and Space Museum — Wright Flyer, Spirit of St. Louis, Apollo 11",
        "National Museum of Natural History — Hope Diamond, Hall of Human Origins",
        "National Museum of American History — Star-Spangled Banner, First Ladies' Gowns",
        "National Museum of African American History and Culture — Emmett Till Memorial",
        "National Zoo — giant pandas, American bison",
        "Hirshhorn Museum — modern and contemporary art, sculpture garden",
        "National Portrait Gallery — presidential portraits, Obama portraits",
        "Smithsonian Castle — the original 1855 institution building",
    ],
    "kennedy space center": [
        "Space Shuttle Atlantis — see Atlantis tilted at 43° with payload bay doors open",
        "Saturn V Rocket — massive moon rocket hanging in the Apollo/Saturn V Center",
        "Heroes & Legends — U.S. Astronaut Hall of Fame with 4D theater",
        "Shuttle Launch Experience — simulated vertical launch to orbit",
        "Gateway: The Deep Space Launch Complex — SpaceX, Blue Origin, Artemis exhibits",
        "Apollo 8 Firing Room — recreated launch control with actual consoles",
        "Rocket Garden — walk among Mercury, Gemini, and Apollo-era rockets",
        "Astronaut Training Experience — hands-on simulators and Mars colony mission",
    ],

    # --- Zoos & Aquariums ---
    "san diego zoo": [
        "Africa Rocks — penguins, baboons, and cichlids across African biomes",
        "Elephant Odyssey — elephants, jaguars, and California condors",
        "Panda Trek — giant pandas and red pandas in bamboo habitat",
        "Lost Forest — okapi, hippos, bonobos, and botanical gardens",
        "Northern Frontier — polar bears and arctic aviary",
        "Australian Outback — koalas, tree kangaroos, Tasmanian devils",
        "Skyfari Aerial Tram — ride across the park canopy",
        "Guided Bus Tour — 35-minute double-decker loop of the full zoo",
    ],
    "bronx zoo": [
        "JungleWorld — indoor Asian rainforest with gibbons, leopards, flying foxes",
        "Congo Gorilla Forest — 6.5-acre habitat with 20+ western lowland gorillas",
        "Tiger Mountain — Amur tigers in a naturalistic taiga setting",
        "Madagascar! — ring-tailed lemur exhibit simulating spiny forest",
        "African Plains — lions, zebras, giraffes in recreated savanna",
        "World of Birds — free-flight walkthrough atrium spanning continents",
        "Butterfly Garden — seasonal walkthrough with native species",
        "Wild Asia Monorail — elevated 2-mile ride over Asian habitats",
    ],

    # --- National Parks ---
    "yellowstone national park": [
        "Old Faithful — predictable geyser erupting every 90 minutes ±10 min",
        "Grand Prismatic Spring — 370 ft wide hot spring, rainbow microbial mats",
        "Mammoth Hot Springs — travertine terraces with elk grazing",
        "Grand Canyon of the Yellowstone — 20-mile canyon, 308 ft Lower Falls",
        "Lamar Valley — wolf and grizzly bear watching at dawn/dusk",
        "Hayden Valley — bison herds and trumpeter swans along the Yellowstone River",
        "Norris Geyser Basin — hottest and most dynamic thermal area in the park",
        "Yellowstone Lake — largest high-elevation lake in North America, 136 sq miles",
    ],
    "yosemite national park": [
        "Yosemite Valley — granite monoliths, meadows, and the Merced River",
        "Half Dome — 8,842 ft granite dome, iconic 15-mile round-trip hike",
        "El Capitan — 3,000 ft vertical granite wall, world's largest monolith",
        "Glacier Point — panoramic overlook of Half Dome and Yosemite Falls",
        "Yosemite Falls — 2,425 ft in three tiers, tallest in North America",
        "Mariposa Grove — 500+ mature giant sequoias including Grizzly Giant",
        "Tuolumne Meadows — high-alpine meadow at 8,600 ft with dome formations",
        "Mist Trail — climb 600 granite steps beside Vernal and Nevada Falls",
    ],
    "grand canyon national park": [
        "South Rim — Mather Point, Yavapai Observation Station, rim trail",
        "Bright Angel Trail — 9.5-mile descent to the Colorado River",
        "Desert View Watchtower — 70 ft stone tower with panoramic canyon views",
        "North Rim — higher, cooler, and less crowded rim experience",
        "Havasu Falls — turquoise travertine waterfalls in Havasupai Reservation (permit)",
        "Colorado River Rafting — multi-day whitewater trips through the Inner Gorge",
        "Grand Canyon Skywalk — glass bridge 4,000 ft above the canyon floor",
        "Phantom Ranch — historic lodge at the bottom, mule ride or hike in",
    ],
    "zion national park": [
        "Angels Landing — 1,488 ft chains-section climb, iconic spine ridge",
        "The Narrows — walk upstream through the Virgin River slot canyon",
        "Emerald Pools — waterfall-fed pools via 3 trails from Zion Lodge",
        "Observation Point — 6,508 ft plateau view, 2,000 ft above canyon floor",
        "Canyon Overlook Trail — 1-mile easy hike with postcard views",
        "Zion Canyon Scenic Drive — shuttle-only canyon road past Court of the Patriarchs",
        "Kolob Canyons — red-rock finger canyons in the northwest section",
        "The Subway — tubular slot canyon requiring permit and technical gear",
    ],
    "great smoky mountains national park": [
        "Clingmans Dome — 6,643 ft observation tower, highest point on the AT",
        "Cades Cove — 11-mile wildlife loop with deer, bear, and 1820s homesteads",
        "Roaring Fork Motor Nature Trail — 5.5-mile one-way through old-growth forest",
        "Alum Cave Trail — hike to Arch Rock and Inspiration Point via 4.6-mile ascent",
        "Laurel Falls — paved 2.6-mile hike to 80 ft cascade waterfall",
        "Newfound Gap — straddle the TN/NC line on the Appalachian Trail",
        "Elkmont Historic District — abandoned 1920s Appalachian Club cabins",
        "Cataloochee Valley — elk herd reintroduced in 2001, historic structures",
    ],
    "rocky mountain national park": [
        "Trail Ridge Road — highest continuous paved road in the U.S. at 12,183 ft",
        "Bear Lake — glacial cirque lake with 0.5-mile accessible loop trail",
        "Alberta Falls — 30 ft waterfall via 1.7-mile forested trail from Bear Lake",
        "Longs Peak — 14,259 ft summit with challenging Keyhole Route",
        "Moraine Park — elk bugling in fall, meadow loop for wildlife",
        "Emerald Lake — alpine lake reached via 3.6-mile trail past Nymph Lake",
        "Alpine Visitor Center — highest visitor center in the NPS at 11,796 ft",
        "Chasm Falls — 25 ft waterfall off Old Fall River Road, easy pull-off",
    ],

    # --- Festivals & City Tours ---
    "new orleans": [
        "French Quarter — Jackson Square, Café du Monde, Bourbon Street stroll",
        "Garden District — antebellum mansions, Lafayette Cemetery No. 1",
        "National WWII Museum — 6 pavilions, immersive Pacific and European theaters",
        "Mardi Gras World — behind-the-scenes float-building warehouse tour",
        "St. Louis Cathedral — oldest continuously active cathedral in the U.S.",
        "Frenchmen Street — live jazz every night, local art market",
        "Steamboat Natchez — paddle-wheel cruise on the Mississippi River",
        "City Park — 1,300 acres, sculpture garden, and live oak groves",
    ],
    "san antonio": [
        "The Alamo — 18th-century mission fortress and Texas Revolution site",
        "San Antonio River Walk — 15 miles of river-level paths with dining and shops",
        "San Antonio Missions National Historical Park — 4 Spanish colonial missions, UNESCO",
        "Pearl District — breweries, farmers market, and boutique shopping along the river",
        "Tower of the Americas — 750 ft observation tower with revolving restaurant",
        "San Antonio Museum of Art — ancient Mediterranean, Latin American, and Asian galleries",
        "Natural Bridge Caverns — largest known commercial cavern in Texas",
        "Japanese Tea Garden — restored 1917 quarry garden with koi ponds and pagoda",
    ],
}


def _classify_venue(name: str, body: str) -> str:
    """Classify venue type from name and search result bodies.

    Venue name keywords receive 3× weight to prevent body text from
    overriding obvious classifications (e.g. Busch Gardens → theme_park
    even when search results mention animals/gardens).

    When the venue name itself carries no signal (no keyword matches
    in the name), body text alone determines the type — but only up
    to a threshold. Without a strong body-text signal, a generic
    destination defaults to city_tour rather than letting low-signal
    keyword matches (e.g. incidental mentions of nearby theme parks)
    misclassify a city as a theme park.
    """
    name_lower = name.lower()
    body_lower = body.lower()
    scores: dict[str, int] = {}
    for vtype, keywords in _VENUE_CLASSIFIERS:
        name_score = sum(3 for kw in keywords if kw in name_lower)
        body_score = sum(1 for kw in keywords if kw in body_lower)
        scores[vtype] = name_score + body_score

    # Separate name-driven vs body-only scores to detect when the
    # venue name itself gives no signal about the destination type.
    name_scores: dict[str, int] = {}
    for vtype, keywords in _VENUE_CLASSIFIERS:
        name_scores[vtype] = sum(3 for kw in keywords if kw in name_lower)

    if not any(scores.values()):
        return "general"

    # When the venue name carries no classification signal whatsoever,
    # the destination is inherently generic (a city, region, or vague
    # place name). Body text alone must never classify a generic
    # destination as a specific venue type like theme_park, museum,
    # zoo, or national_park — only city_tour, festival, or general
    # are valid for generic destinations.
    name_has_signal = any(v > 0 for v in name_scores.values())
    if not name_has_signal:
        if scores.get("festival", 0) > 0:
            return "festival"
        if scores.get("city_tour", 0) > 0:
            return "city_tour"
        return "general"

    return max(scores, key=lambda k: scores[k])  # type: ignore[no-any-return]


def _lookup_curated_attractions(venue_name: str, location: str = "") -> list[str]:
    """Look up pre-curated attractions from the knowledge base and database.

    Priority order:
    1. Hardcoded _VENUE_ATTRACTIONS dict (fast, curated strings)
    2. SQLite venue_attractions table (dynamic, queryable)
    3. Empty list (fall through to web search extraction)

    Args:
        venue_name: Normalized venue name from planner (e.g. "Busch Gardens").
        location: Optional city/region disambiguator (e.g. "Tampa").

    Returns:
        List of attraction strings, or empty list.
    """
    venue_lower = venue_name.strip().lower()
    location_lower = location.strip().lower() if location else ""

    # ── Tier 1: Hardcoded knowledge base ──────────────────────────────
    # 1a. Exact match on "venue location" combined key
    if location_lower:
        combined_key = f"{venue_lower} {location_lower}"
        if combined_key in _VENUE_ATTRACTIONS:
            logger.info("Curated attractions found for %r (exact combined)", combined_key)
            return list(_VENUE_ATTRACTIONS[combined_key])

    # 1b. Try each key that contains both venue name and location
    if location_lower:
        for key, attractions in _VENUE_ATTRACTIONS.items():
            if venue_lower in key and location_lower in key:
                logger.info("Curated attractions found for %r (combined fuzzy: %r)", venue_name, key)
                return list(attractions)

    # 1c. Exact match on venue name alone (no location in key)
    for key, attractions in _VENUE_ATTRACTIONS.items():
        if key == venue_lower:
            logger.info("Curated attractions found for %r (exact venue)", venue_name)
            return list(attractions)

    # 1d. Substring match — key contains the venue name
    for key, attractions in _VENUE_ATTRACTIONS.items():
        if venue_lower in key or key in venue_lower:
            logger.info("Curated attractions found for %r (fuzzy: %r)", venue_name, key)
            return list(attractions)

    # 1e. Single-word partial match (e.g. "busch gardens" matching "busch gardens tampa")
    venue_words = set(venue_lower.split())
    if len(venue_words) >= 2:
        for key, attractions in _VENUE_ATTRACTIONS.items():
            key_words = set(key.split())
            overlap = venue_words & key_words
            if len(overlap) >= 2 and overlap == venue_words:
                logger.info("Curated attractions found for %r (word-overlap: %r)", venue_name, key)
                return list(attractions)

    # ── Tier 2: SQLite database fallback ──────────────────────────────
    db_attractions = db.lookup_venue_attractions(venue_name, location, limit=12)
    if db_attractions:
        formatted = []
        for a in db_attractions:
            desc = a.get("description", "") or ""
            if desc:
                formatted.append(f"{a['name']} — {desc}")
            else:
                formatted.append(a["name"])
        logger.info(
            "DB attractions found for %r (location=%r): %d results",
            venue_name, location, len(formatted),
        )
        return formatted

    return []


def _extract_attraction_names(text: str) -> list[str]:
    """Extract likely attraction names from a text blurb."""
    import re

    # Match capitalized phrases that look like proper names (2-4 words)
    matches = re.findall(r'\b([A-Z][a-z]+(?:\s+(?:of|the|and|in|at|for)\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?(?:\s+[A-Z][a-z]+)?)\b', text)
    # Filter out noise
    skip = {"the", "and", "of", "for", "with", "this", "that", "your", "from", "here"}
    results: list[str] = []
    for m in matches:
        clean = m.strip()
        if len(clean) > 4 and clean.lower() not in skip and not clean.lower().startswith(("http", "www")):
            results.append(clean)
    return results[:5]


def _extract_crowd_tip(text: str) -> str | None:
    """Extract a crowd-avoidance tip from text."""
    import re

    patterns = [
        r'(arrive\s+\w+\s+(?:before|after|at)\s+[^.]+)',
        r'(best\s+time\s+to\s+visit\s+is\s+[^.]+)',
        r'(avoid\s+\w+\s+(?:crowds?|lines?|queues?)\s+[^.]+)',
        r'(go\s+(?:early|late|during)\s+[^.]+)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip().capitalize()
    return None


def _extract_restaurant_name(title: str, body: str) -> str | None:
    """Extract a restaurant name from search result title/body.

    Filters out garbage results like 'Best', 'Top 10 Restaurants',
    'Find Hotels with a Restaurant', etc. that are search aggregator pages.
    """
    import re

    # Common patterns in DuckDuckGo results
    # Title often contains "Restaurant Name — Cuisine" or "Restaurant Name |"
    title_match = re.match(r'^(.+?)\s*[-–—|·•]', title)
    if title_match:
        candidate = title_match.group(1).strip()
        if _is_valid_restaurant_name(candidate):
            return candidate

    # Try capital-word sequences in body
    words = body.split()
    for i in range(len(words) - 2):
        if words[i][0].isupper() and words[i + 1][0].isupper():
            candidate = words[i]
            if _is_valid_restaurant_name(candidate):
                return candidate
    return None


def _is_valid_restaurant_name(name: str) -> bool:
    """Reject restaurant names that look like search aggregator pages."""
    if len(name) < 3 or len(name) > 50:
        return False
    if name.lower().startswith(("http", "www")):
        return False

    garbage = [
        r'^[Bb]est$',                              # "Best"
        r'^[Bb]est[\s\-–—].*[Rr]estaurants?',      # "Best Restaurants ..."
        r'^[Tt]op\s+\d+\s+[Rr]estaurants?',         # "Top 10 Restaurants ..."
        r'^[Tt]he\s+\d+\s+[Bb]est\s',               # "The 10 Best ..."
        r'^[Tt]he\s+[Bb]est\s+\d+',                 # "The Best 10 ..."
        r'^[Ff]ind\s',                              # "Find Hotels..."
        r'^[Hh]otels?\s+with',                      # "Hotels with a Restaurant"
        r'^[Rr]estaurants?\s+[Nn]ear',              # "Restaurants Near ..."
        r'^[Rr]estaurants?\s+[Ii]n',                # "Restaurants in ..."
        r'^[Nn]o\s+[Mm]enu',                        # "No Menu Needed"
        r'^[Ss]earch\s',                            # "Search ..."
        r'^[Bb]ook\s',                              # "Book ..."
        r'^\d+\s+[Rr]estaurants?',                  # "10 Restaurants..."
        r'^\d+\s+[Bb]est\s',                         # "10 Best ..."
        r'^[Hh]ow\s+to\s',                          # "How to ..."
        r'^\$\d+',                                  # "$100 ..."
        r'\b[Hh]otels?\b.*\b[Rr]estaurant\b',      # anything with "Hotel...Restaurant"
    ]
    import re
    for pat in garbage:
        if re.search(pat, name):
            return False

    # "Tampa Inn" could be a real restaurant or a hotel — too ambiguous, reject
    single_word_garbage = {
        "best", "restaurant", "restaurants", "menu",
        "food", "eat", "dining", "dinner", "lunch",
        "reservations", "open", "closed",
    }
    if name.lower() in single_word_garbage:
        return False

    return True


def _extract_hotel_name(title: str, body: str) -> str | None:
    """Extract a hotel name from search result.

    Filters out garbage titles like '4 & 5 Star Tampa Hotel' or
    'Best Hotels In Tampa' that are search result pages, not real hotels.
    """
    import re

    known_chains = [
        "Hyatt", "Marriott", "Hilton", "Holiday Inn", "Best Western",
        "Hampton Inn", "Fairfield", "Courtyard", "Residence Inn", "Sheraton",
        "Westin", "DoubleTree", "Embassy Suites", "Homewood Suites",
        "SpringHill", "TownePlace", "Comfort Inn", "Quality Inn",
        "La Quinta", "Days Inn", "Wyndham", "Ramada", "Radisson",
        "Motel 6", "Super 8", "Red Roof", "Econo Lodge", "Microtel",
        "Drury", "Omni", "Loews", "Ritz-Carlton", "Four Seasons",
        "Waldorf", "St. Regis", "JW Marriott", "Renaissance", "Crowne Plaza",
        "InterContinental", "Kimpton", "Aloft", "Element", "Autograph",
        "Tribute", "Moxy", "AC Hotels", "Le Méridien", "W Hotels",
        "Grand Hyatt", "Hyatt Regency", "Hyatt Place", "Hyatt House",
        "Hilton Garden", "Hampton by Hilton", "Tru by Hilton", "Home2 Suites",
        "Curio", "Tapestry", "Canopy", "Tempo",
    ]
    combined = f"{title} {body}"

    for chain in known_chains:
        pat = re.compile(rf'\b({chain}\s+[\w\s]{{2,50}}?)\b(?:[-–—]|\s*$|\s+hotel|\s+inn|\s+suites?|\s+resort)', re.IGNORECASE)
        m = pat.search(combined)
        if m:
            candidate = m.group(1).strip()
            if not _is_garbage_hotel_title(candidate):
                return candidate

    # Fallback: title prefix but validate it's not garbage
    title_match = re.match(r'^(.+?)\s*[-–—|·•]', title)
    if title_match:
        candidate = title_match.group(1).strip()
        if 5 < len(candidate) < 60 and not _is_garbage_hotel_title(candidate):
            return candidate
    return None


def _is_garbage_hotel_title(name: str) -> bool:
    """Reject titles that look like search-result pages, not real hotel names."""
    garbage_patterns = [
        r'^\d+\s*[&]\s*\d+\s*[Ss]tar',          # "4 & 5 Star ..."
        r'^[Bb]est\s+[Hh]otels?\b',              # "Best Hotels In ..."
        r'^[Tt]he\s+\d+\s+[Bb]est\b',            # "The 10 Best ..."
        r'^[Tt]op\s+\d+\s+[Hh]otels?\b',         # "Top 10 Hotels ..."
        r'^[Hh]otels?\s+in\b',                    # "Hotels in Tampa"
        r'^\d+\s+[Hh]otels?\b',                   # "15 Hotels ..."
        r'^[Cc]heap\b',                          # "Cheap Hotels..."
        r'^[Aa]ffordable\b',                     # "Affordable Hotels..."
        r'^[Ll]uxury\s+[Hh]otels?\b',            # "Luxury Hotels..."
        r'^[Bb]ook\s',                           # "Book Hotels..."
        r'^[Ss]earch\s',                         # "Search Hotels..."
        r'^[Ff]ind\s',                           # "Find Hotels..."
        r'\$\d+',                                # "$100 Hotels..."
        r'^\d{4}\s',                             # "2024 Hotels..."
        r'^[Mm]ap\s+of\b',                       # "Map of ..."
        r'^[Rr]eviews?\s+of\b',                  # "Reviews of ..."
        r'^[Ii]mages?\s+of\b',                   # "Images of ..."
    ]
    import re
    for pat in garbage_patterns:
        if re.search(pat, name):
            return True
    return False


# Curated hotel fallbacks for common destination cities when search
# returns only garbage results.
_HOTEL_FALLBACKS: dict[str, list[dict[str, Any]]] = {
    "tampa": [
        {"name": "Tampa Marriott Water Street", "star_rating": 4, "price_range": "$$$",
         "location": "Downtown Tampa — waterfront", "highlights": "Pool, Fitness center, Free WiFi, On-site restaurant",
         "booking_url": "https://www.marriott.com"},
        {"name": "Hyatt Place Tampa Downtown", "star_rating": 3, "price_range": "$$",
         "location": "Downtown Tampa — near Riverwalk", "highlights": "Free breakfast, Pool, Free WiFi",
         "booking_url": "https://www.hyatt.com"},
        {"name": "Hampton Inn & Suites Tampa Busch Gardens Area", "star_rating": 3, "price_range": "$$",
         "location": "Near Busch Gardens — 1 mile from park entrance", "highlights": "Free breakfast, Pool, Free WiFi, Free parking",
         "booking_url": "https://www.hilton.com"},
    ],
    "orlando": [
        {"name": "Hyatt Regency Orlando", "star_rating": 4, "price_range": "$$$",
         "location": "International Drive — near Universal", "highlights": "Pool, Spa, Fitness center, Free WiFi",
         "booking_url": "https://www.hyatt.com"},
        {"name": "JW Marriott Orlando Grande Lakes", "star_rating": 5, "price_range": "$$$$",
         "location": "Grande Lakes — resort setting", "highlights": "Pool, Spa, Golf course, Free WiFi, On-site restaurant",
         "booking_url": "https://www.marriott.com"},
        {"name": "Hilton Orlando Buena Vista Palace", "star_rating": 4, "price_range": "$$$",
         "location": "Disney Springs area", "highlights": "Pool, Free WiFi, On-site restaurant, Disney shuttle",
         "booking_url": "https://www.hilton.com"},
    ],
    "miami": [
        {"name": "Loews Miami Beach Hotel", "star_rating": 5, "price_range": "$$$$",
         "location": "South Beach — oceanfront", "highlights": "Pool, Spa, Beach access, Free WiFi, On-site restaurant",
         "booking_url": "https://www.loewshotels.com"},
        {"name": "Kimpton EPIC Hotel", "star_rating": 5, "price_range": "$$$$",
         "location": "Downtown Miami — waterfront", "highlights": "Pool, Spa, Rooftop bar, Free WiFi",
         "booking_url": "https://www.kimptonhotels.com"},
        {"name": "Hampton Inn & Suites Miami Brickell Downtown", "star_rating": 3, "price_range": "$$",
         "location": "Brickell — downtown financial district", "highlights": "Free breakfast, Pool, Free WiFi",
         "booking_url": "https://www.hilton.com"},
    ],
    "atlanta": [
        {"name": "Atlanta Marriott Marquis", "star_rating": 4, "price_range": "$$$",
         "location": "Downtown Atlanta — Peachtree Center", "highlights": "Pool, Fitness center, Free WiFi, On-site restaurant",
         "booking_url": "https://www.marriott.com"},
        {"name": "Hyatt Regency Atlanta", "star_rating": 4, "price_range": "$$$",
         "location": "Downtown Atlanta — Peachtree Street", "highlights": "Pool, Free WiFi, On-site restaurant",
         "booking_url": "https://www.hyatt.com"},
        {"name": "Hampton Inn & Suites Atlanta Downtown", "star_rating": 3, "price_range": "$$",
         "location": "Downtown Atlanta — near Centennial Park", "highlights": "Free breakfast, Free WiFi, Fitness center",
         "booking_url": "https://www.hilton.com"},
    ],
    "new york": [
        {"name": "The Westin New York at Times Square", "star_rating": 4, "price_range": "$$$$",
         "location": "Midtown Manhattan — Times Square", "highlights": "Fitness center, Free WiFi, On-site restaurant",
         "booking_url": "https://www.marriott.com"},
        {"name": "Hyatt Grand Central New York", "star_rating": 4, "price_range": "$$$",
         "location": "Midtown East — near Grand Central Terminal", "highlights": "Fitness center, Free WiFi, On-site restaurant",
         "booking_url": "https://www.hyatt.com"},
        {"name": "Hampton Inn Manhattan/Times Square South", "star_rating": 3, "price_range": "$$$",
         "location": "Midtown Manhattan — Times Square South", "highlights": "Free breakfast, Free WiFi, Fitness center",
         "booking_url": "https://www.hilton.com"},
    ],
    "paris": [
        {"name": "Pullman Paris Tour Eiffel", "star_rating": 4, "price_range": "$$$$",
         "location": "Eiffel Tower district — views of the tower", "highlights": "Free WiFi, On-site restaurant, Fitness center",
         "booking_url": "https://www.accor.com"},
        {"name": "Hôtel Le Marais by Hyatt", "star_rating": 4, "price_range": "$$$",
         "location": "Le Marais — historic district", "highlights": "Free WiFi, Boutique hotel, Central location",
         "booking_url": "https://www.hyatt.com"},
    ],
}


def _infer_cuisine(text: str) -> str:
    """Infer cuisine type from text."""
    text_lower = text.lower()
    cuisines = [
        ("italian", "Italian"),
        ("mexican", "Mexican"),
        ("japanese", "Japanese"),
        ("chinese", "Chinese"),
        ("american", "American"),
        ("french", "French"),
        ("thai", "Thai"),
        ("indian", "Indian"),
        ("mediterranean", "Mediterranean"),
        ("seafood", "Seafood"),
        ("steakhouse", "Steakhouse"),
        ("bbq", "BBQ"),
        ("barbecue", "BBQ"),
        ("korean", "Korean"),
        ("vietnamese", "Vietnamese"),
        ("sushi", "Japanese"),
        ("pizza", "Italian"),
        ("burger", "American"),
    ]
    scores: dict[str, int] = {}
    for keyword, cuisine in cuisines:
        scores[cuisine] = scores.get(cuisine, 0) + text_lower.count(keyword)
    if not any(scores.values()):
        return "American"
    return max(scores, key=lambda k: scores[k])  # type: ignore[no-any-return]


def _infer_price(text: str) -> str:
    """Infer price range ($-$$$$) from text."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["expensive", "fine dining", "upscale", "luxury", "gourmet"]):
        return "$$$"
    if any(w in text_lower for w in ["moderate", "mid-range", "casual dining", "$$"]):
        return "$$"
    if any(w in text_lower for w in ["cheap", "budget", "affordable", "inexpensive", "fast food"]):
        return "$"
    return "$$"


def _extract_amenities(text: str) -> str:
    """Extract hotel amenities from text."""
    amenities: list[str] = []
    amenity_keywords = [
        ("free breakfast", "Free breakfast"),
        ("pool", "Pool"),
        ("fitness center", "Fitness center"),
        ("gym", "Fitness center"),
        ("free wifi", "Free WiFi"),
        ("airport shuttle", "Airport shuttle"),
        ("free parking", "Free parking"),
        ("pet friendly", "Pet friendly"),
        ("spa", "Spa"),
        ("restaurant", "On-site restaurant"),
    ]
    text_lower = text.lower()
    seen: set[str] = set()
    for kw, label in amenity_keywords:
        if kw in text_lower and label.lower() not in seen:
            seen.add(label.lower())
            amenities.append(label)
    return ", ".join(amenities) if amenities else "Pool, Free WiFi"


def _extract_duration(text: str) -> list[str]:
    """Extract time duration phrases from text."""
    import re

    patterns = [
        r'(\d+[–-]\d+\s*(?:hour|hr|minute|min)s?\s*(?:drive|trip|journey)?)',
        r'(\d+\s*(?:hour|hr|minute|min)s?\s*(?:drive|trip|journey)?)',
        r'(approximately\s+\d+[–-]?\d*\s*(?:hour|hr|minute|min)s?)',
    ]
    results: list[str] = []
    for pat in patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        results.extend(matches)
    return results


def _parse_minutes_raw(duration_str: str) -> int:
    """Parse a duration string like '1 hour 15 minutes' or '13 min' into total minutes.

    Returns 0 when the string cannot be parsed meaningfully.
    """
    import re

    total = 0
    h_match = re.search(r'(\d+)\s*(?:hour|hr)', duration_str, re.IGNORECASE)
    m_match = re.search(r'(\d+)\s*(?:minute|min)', duration_str, re.IGNORECASE)
    if h_match:
        total += int(h_match.group(1)) * 60
    if m_match:
        total += int(m_match.group(1))
    return total
