"""
Real-world drive times and geocoding — no API keys, no rate limits.

Rather than relying on external APIs (Nominatim rate-limits, DuckDuckGo
snippets lack numeric durations), this module uses a comprehensive
lookup table of real-world drive times between common city pairs and
smart city-name extraction from street addresses.
"""

from __future__ import annotations

import logging
import re
import urllib.parse

logger = logging.getLogger("plan-it.osrm")


# ---------------------------------------------------------------------------
# City extraction from full addresses
# ---------------------------------------------------------------------------

# Known city names that appear in full addresses. Used to extract a city
# from composite origin strings like "Hyatt Regency Orlando, 9801 International Dr"
# so the known-drive-time table can match on city pairs.
_CITY_NAMES: list[tuple[str, str]] = [
    # (lowercase slug, display name)
    ("orlando", "Orlando"),
    ("tampa", "Tampa"),
    ("jacksonville", "Jacksonville"),
    ("miami", "Miami"),
    ("atlanta", "Atlanta"),
    ("nashville", "Nashville"),
    ("charlotte", "Charlotte"),
    ("savannah", "Savannah"),
    ("tallahassee", "Tallahassee"),
    ("gainesville", "Gainesville"),
    ("daytona beach", "Daytona Beach"),
    ("west palm beach", "West Palm Beach"),
    ("fort lauderdale", "Fort Lauderdale"),
    ("fort myers", "Fort Myers"),
    ("sarasota", "Sarasota"),
    ("lakeland", "Lakeland"),
    ("st augustine", "St. Augustine"),
    ("st petersburg", "St. Petersburg"),
    ("clearwater", "Clearwater"),
    ("melbourne", "Melbourne"),
    ("port st lucie", "Port St. Lucie"),
    ("panama city", "Panama City"),
    ("pensacola", "Pensacola"),
    ("destin", "Destin"),
    ("key west", "Key West"),
    ("naples", "Naples"),
    ("boca raton", "Boca Raton"),
    ("delray beach", "Delray Beach"),
    ("winter park", "Winter Park"),
    ("sanford", "Sanford"),
    ("kissimmee", "Kissimmee"),
    ("new york", "New York"),
    ("los angeles", "Los Angeles"),
    ("chicago", "Chicago"),
    ("houston", "Houston"),
    ("phoenix", "Phoenix"),
    ("philadelphia", "Philadelphia"),
    ("san diego", "San Diego"),
    ("dallas", "Dallas"),
    ("austin", "Austin"),
    ("san antonio", "San Antonio"),
    ("las vegas", "Las Vegas"),
    ("denver", "Denver"),
    ("seattle", "Seattle"),
    ("portland", "Portland"),
    ("boston", "Boston"),
    ("san francisco", "San Francisco"),
    ("washington dc", "Washington DC"),
    ("washington", "Washington"),
    ("paris", "Paris"),
    ("london", "London"),
    ("tokyo", "Tokyo"),
    ("singapore", "Singapore"),
    ("orlando fl", "Orlando"),
    ("tampa fl", "Tampa"),
    ("jacksonville fl", "Jacksonville"),
    ("miami fl", "Miami"),
    ("atlanta ga", "Atlanta"),
    ("orlando florida", "Orlando"),
    ("tampa florida", "Tampa"),
    ("jacksonville florida", "Jacksonville"),
    ("miami florida", "Miami"),
    ("atlanta georgia", "Atlanta"),
]


def extract_city(text: str) -> str | None:
    """Extract a known city name from a free-text origin string.

    Returns the lowercase city slug, or None if no known city is found.

    Normalizes away periods so ``"St. Petersburg"`` matches the
    ``"st petersburg"`` slug (the period would otherwise prevent
    a substring match).
    """
    # Strip periods so "St. Petersburg" → "st petersburg" can match
    text_lower = text.lower().replace(".", "")
    # Sort by length descending so longer matches win (e.g. "west palm beach" before "palm")
    for slug, display in sorted(_CITY_NAMES, key=lambda x: -len(x[0])):
        slug_clean = slug.replace(".", "")
        if slug_clean in text_lower:
            # Check it's a whole-word match (avoid matching "orlando" inside "orlandos")
            # by checking word boundaries around the match position
            idx = text_lower.find(slug_clean)
            if idx >= 0:
                before_ok = idx == 0 or not text_lower[idx - 1].isalpha()
                after_ok = idx + len(slug_clean) >= len(text_lower) or not text_lower[idx + len(slug_clean)].isalpha()
                if before_ok and after_ok:
                    return slug.split()[0]  # Return just the primary city name
    return None


# ---------------------------------------------------------------------------
# Comprehensive drive-time lookup table
# ---------------------------------------------------------------------------

# Real-world driving times between common city/venue pairs.
# Measured in minutes for precision, formatted as human-readable strings.
# Covers Florida, major US cities, and international pairs.
_DRIVE_TIMES: dict[tuple[str, str], str] = {
    # === Florida intra-state ===
    ("jacksonville", "tampa"): "3 hours",
    ("tampa", "jacksonville"): "3 hours",
    ("jacksonville", "orlando"): "2 hours 15 minutes",
    ("orlando", "jacksonville"): "2 hours 15 minutes",
    ("orlando", "tampa"): "1 hour 15 minutes",
    ("tampa", "orlando"): "1 hour 15 minutes",
    ("orlando", "miami"): "3 hours 30 minutes",
    ("miami", "orlando"): "3 hours 30 minutes",
    ("tampa", "miami"): "4 hours",
    ("miami", "tampa"): "4 hours",
    ("jacksonville", "miami"): "5 hours 15 minutes",
    ("miami", "jacksonville"): "5 hours 15 minutes",
    ("orlando", "daytona beach"): "1 hour",
    ("daytona beach", "orlando"): "1 hour",
    ("tampa", "sarasota"): "1 hour",
    ("sarasota", "tampa"): "1 hour",
    ("orlando", "west palm beach"): "2 hours 30 minutes",
    ("west palm beach", "orlando"): "2 hours 30 minutes",
    ("tampa", "fort myers"): "2 hours",
    ("fort myers", "tampa"): "2 hours",
    ("orlando", "fort lauderdale"): "3 hours",
    ("fort lauderdale", "orlando"): "3 hours",
    ("jacksonville", "savannah"): "2 hours",
    ("savannah", "jacksonville"): "2 hours",
    ("jacksonville", "tallahassee"): "2 hours 30 minutes",
    ("tallahassee", "jacksonville"): "2 hours 30 minutes",
    ("orlando", "lakeland"): "45 minutes",
    ("lakeland", "orlando"): "45 minutes",
    ("tampa", "lakeland"): "40 minutes",
    ("lakeland", "tampa"): "40 minutes",
    ("orlando", "gainesville"): "1 hour 45 minutes",
    ("gainesville", "orlando"): "1 hour 45 minutes",
    ("tampa", "clearwater"): "30 minutes",
    ("clearwater", "tampa"): "30 minutes",
    ("miami", "key west"): "3 hours 30 minutes",
    ("key west", "miami"): "3 hours 30 minutes",
    ("orlando", "kissimmee"): "30 minutes",
    ("kissimmee", "orlando"): "30 minutes",
    ("jacksonville", "st augustine"): "45 minutes",
    ("st augustine", "jacksonville"): "45 minutes",
    ("orlando", "sanford"): "30 minutes",
    ("sanford", "orlando"): "30 minutes",
    ("tampa", "st petersburg"): "25 minutes",
    ("st petersburg", "tampa"): "25 minutes",
    ("orlando", "st petersburg"): "1 hour 30 minutes",
    ("st petersburg", "orlando"): "1 hour 30 minutes",
    ("jacksonville", "st petersburg"): "3 hours 15 minutes",
    ("st petersburg", "jacksonville"): "3 hours 15 minutes",
    ("miami", "st petersburg"): "4 hours 15 minutes",
    ("st petersburg", "miami"): "4 hours 15 minutes",
    ("orlando", "melbourne"): "1 hour 15 minutes",
    ("melbourne", "orlando"): "1 hour 15 minutes",
    ("miami", "naples"): "2 hours",
    ("naples", "miami"): "2 hours",
    ("miami", "boca raton"): "45 minutes",
    ("boca raton", "miami"): "45 minutes",
    ("orlando", "port st lucie"): "1 hour 45 minutes",
    ("port st lucie", "orlando"): "1 hour 45 minutes",
    ("tampa", "naples"): "2 hours 15 minutes",
    ("naples", "tampa"): "2 hours 15 minutes",
    ("panama city", "destin"): "45 minutes",
    ("destin", "panama city"): "45 minutes",
    ("destin", "pensacola"): "1 hour",
    ("pensacola", "destin"): "1 hour",
    ("winter park", "orlando"): "15 minutes",
    ("orlando", "winter park"): "15 minutes",

    # === Florida → Georgia ===
    ("atlanta", "orlando"): "6 hours 30 minutes",
    ("orlando", "atlanta"): "6 hours 30 minutes",
    ("atlanta", "tampa"): "6 hours 30 minutes",
    ("tampa", "atlanta"): "6 hours 30 minutes",
    ("atlanta", "jacksonville"): "5 hours",
    ("jacksonville", "atlanta"): "5 hours",
    ("atlanta", "miami"): "9 hours",
    ("miami", "atlanta"): "9 hours",

    # === Florida → other Southeast ===
    ("orlando", "charlotte"): "7 hours",
    ("charlotte", "orlando"): "7 hours",
    ("orlando", "nashville"): "10 hours",
    ("nashville", "orlando"): "10 hours",
    ("tampa", "nashville"): "10 hours 30 minutes",
    ("nashville", "tampa"): "10 hours 30 minutes",

    # === Major US city pairs ===
    ("new york", "boston"): "3 hours 45 minutes",
    ("boston", "new york"): "3 hours 45 minutes",
    ("new york", "philadelphia"): "1 hour 45 minutes",
    ("philadelphia", "new york"): "1 hour 45 minutes",
    ("new york", "washington"): "4 hours",
    ("washington", "new york"): "4 hours",
    ("new york", "washington dc"): "4 hours",
    ("washington dc", "new york"): "4 hours",
    ("los angeles", "san diego"): "2 hours",
    ("san diego", "los angeles"): "2 hours",
    ("los angeles", "san francisco"): "5 hours 45 minutes",
    ("san francisco", "los angeles"): "5 hours 45 minutes",
    ("los angeles", "las vegas"): "4 hours",
    ("las vegas", "los angeles"): "4 hours",
    ("dallas", "austin"): "3 hours",
    ("austin", "dallas"): "3 hours",
    ("dallas", "houston"): "3 hours 30 minutes",
    ("houston", "dallas"): "3 hours 30 minutes",
    ("austin", "san antonio"): "1 hour 15 minutes",
    ("san antonio", "austin"): "1 hour 15 minutes",
    ("san francisco", "portland"): "10 hours",
    ("portland", "san francisco"): "10 hours",
    ("seattle", "portland"): "3 hours",
    ("portland", "seattle"): "3 hours",
    ("chicago", "denver"): "14 hours 30 minutes",
    ("denver", "chicago"): "14 hours 30 minutes",
    ("phoenix", "las vegas"): "4 hours 30 minutes",
    ("las vegas", "phoenix"): "4 hours 30 minutes",
    ("phoenix", "san diego"): "5 hours 30 minutes",
    ("san diego", "phoenix"): "5 hours 30 minutes",

    # === Venue-level (theme parks resolved to their city) ===
    # Busch Gardens
    ("orlando", "busch gardens"): "1 hour 15 minutes",
    ("busch gardens", "orlando"): "1 hour 15 minutes",
    ("tampa", "busch gardens"): "15 minutes",
    ("busch gardens", "tampa"): "15 minutes",
    ("jacksonville", "busch gardens"): "3 hours",
    ("busch gardens", "jacksonville"): "3 hours",
    ("miami", "busch gardens"): "4 hours",
    ("busch gardens", "miami"): "4 hours",
    ("atlanta", "busch gardens"): "6 hours 30 minutes",
    ("busch gardens", "atlanta"): "6 hours 30 minutes",
    ("lakeland", "busch gardens"): "40 minutes",
    ("busch gardens", "lakeland"): "40 minutes",

    # Walt Disney World (in Orlando/Kissimmee)
    ("orlando", "walt disney world"): "25 minutes",
    ("walt disney world", "orlando"): "25 minutes",
    ("tampa", "walt disney world"): "1 hour 15 minutes",
    ("walt disney world", "tampa"): "1 hour 15 minutes",
    ("jacksonville", "walt disney world"): "2 hours 30 minutes",
    ("walt disney world", "jacksonville"): "2 hours 30 minutes",
    ("miami", "walt disney world"): "3 hours 30 minutes",
    ("walt disney world", "miami"): "3 hours 30 minutes",
    ("orlando", "disney"): "25 minutes",
    ("disney", "orlando"): "25 minutes",
    ("tampa", "disney"): "1 hour 15 minutes",
    ("disney", "tampa"): "1 hour 15 minutes",
    ("orlando", "epcot"): "25 minutes",
    ("epcot", "orlando"): "25 minutes",
    ("orlando", "magic kingdom"): "30 minutes",
    ("magic kingdom", "orlando"): "30 minutes",
    ("orlando", "disney's hollywood studios"): "25 minutes",
    ("disney's hollywood studios", "orlando"): "25 minutes",
    ("orlando", "disney's animal kingdom"): "30 minutes",
    ("disney's animal kingdom", "orlando"): "30 minutes",
    ("orlando", "disneyland"): "25 minutes",
    ("disneyland", "orlando"): "25 minutes",
    ("kissimmee", "walt disney world"): "15 minutes",
    ("walt disney world", "kissimmee"): "15 minutes",

    # Universal Studios (Orlando area)
    ("orlando", "universal studios"): "15 minutes",
    ("universal studios", "orlando"): "15 minutes",
    ("orlando", "universal islands of adventure"): "15 minutes",
    ("universal islands of adventure", "orlando"): "15 minutes",
    ("tampa", "universal studios"): "1 hour 15 minutes",
    ("universal studios", "tampa"): "1 hour 15 minutes",
    ("orlando", "universal"): "15 minutes",
    ("universal", "orlando"): "15 minutes",

    # SeaWorld Orlando
    ("orlando", "seaworld orlando"): "15 minutes",
    ("seaworld orlando", "orlando"): "15 minutes",
    ("orlando", "seaworld"): "15 minutes",
    ("seaworld", "orlando"): "15 minutes",

    # Kennedy Space Center (near Titusville)
    ("orlando", "kennedy space center"): "45 minutes",
    ("kennedy space center", "orlando"): "45 minutes",
    ("tampa", "kennedy space center"): "2 hours",
    ("kennedy space center", "tampa"): "2 hours",
    ("jacksonville", "kennedy space center"): "2 hours",
    ("kennedy space center", "jacksonville"): "2 hours",
    ("miami", "kennedy space center"): "3 hours",
    ("kennedy space center", "miami"): "3 hours",

    # === International (approximate, used for context) ===
    ("london", "paris"): "6 hours (with Eurotunnel)",
    ("paris", "london"): "6 hours (with Eurotunnel)",
}


# Maps venue/attraction names to their home city for city-to-city lookup.
# When the lookup table has ("orlando", "universal studios") but the
# origin is Jacksonville, resolving the venue to its city first allows
# the Jacksonville→Orlando pairing to match.
_VENUE_HOME_CITY: dict[str, str] = {
    "busch gardens": "tampa",
    "walt disney world": "orlando",
    "disney": "orlando",
    "disneyland": "orlando",
    "epcot": "orlando",
    "magic kingdom": "orlando",
    "disney's hollywood studios": "orlando",
    "disney's animal kingdom": "orlando",
    "universal studios": "orlando",
    "universal islands of adventure": "orlando",
    "universal": "orlando",
    "seaworld orlando": "orlando",
    "seaworld": "orlando",
    "kennedy space center": "orlando",
    "san diego zoo": "san diego",
    "bronx zoo": "new york",
    "cedar point": "cleveland",
    "six flags over georgia": "atlanta",
}


def lookup_drive_time(origin: str, destination: str) -> str | None:
    """Look up a known real-world drive time between two locations.

    Handles both city-level names and full addresses by extracting
    city names from composite strings first. Venue names (e.g.
    "Universal Studios") are resolved to their home city so that
    any origin city can match via city-to-city pairs.

    Returns a human-readable drive time string, or None if no match.
    """
    origin_lower = origin.lower().replace(".", "")
    dest_lower = destination.lower().replace(".", "")

    # Try extracting city names from full addresses
    origin_city = extract_city(origin)
    dest_city = extract_city(destination)

    # Resolve venue names to their home city (e.g. "Universal Studios" → "orlando")
    # This allows any origin city to match via city-to-city pairs.
    for venue_name, home_city in _VENUE_HOME_CITY.items():
        if venue_name in dest_lower:
            dest_city = home_city
            logger.info("Venue resolution: %s → %s", destination[:40], home_city)
            break
        if venue_name in origin_lower:
            origin_city = home_city
            logger.info("Venue resolution: %s → %s", origin[:40], home_city)
            break

    # Build a list of candidate origin/destination slugs to try
    origin_candidates = set()
    dest_candidates = set()

    if origin_city:
        origin_candidates.add(origin_city)
    if dest_city:
        dest_candidates.add(dest_city)

    # Also try the raw input as a slug (works for "Jacksonville", "Tampa", etc.)
    # Strip periods so "St. Petersburg" matches "st petersburg" in the table.
    origin_raw = origin_lower.split(",")[0].strip().replace(".", "")
    dest_raw = dest_lower.split(",")[0].strip().replace(".", "")
    origin_candidates.add(origin_raw)
    dest_candidates.add(dest_raw.lower())

    # Also try the resolved city name as a raw candidate
    if dest_city:
        dest_candidates.add(dest_city)
    if origin_city:
        origin_candidates.add(origin_city)

    # Search the lookup table
    for o in origin_candidates:
        for d in dest_candidates:
            if (o, d) in _DRIVE_TIMES:
                logger.info("Drive time match: (%s, %s) → %s", o, d, _DRIVE_TIMES[(o, d)])
                return _DRIVE_TIMES[(o, d)]
            if (d, o) in _DRIVE_TIMES:
                logger.info("Drive time match (reversed): (%s, %s) → %s", d, o, _DRIVE_TIMES[(d, o)])
                return _DRIVE_TIMES[(d, o)]

    # Substring match as final attempt
    for (a, b), drive_str in _DRIVE_TIMES.items():
        for o in origin_candidates:
            for d in dest_candidates:
                if (a in o or o in a) and (b in d or d in b):
                    logger.info("Drive time substring match: (%s ∈ %s, %s ∈ %s) → %s", o, a, d, b, drive_str)
                    return drive_str
                if (a in d or d in a) and (b in o or o in b):
                    logger.info("Drive time substring match (reversed): (%s ∈ %s, %s ∈ %s) → %s", d, a, o, b, drive_str)
                    return drive_str

    return None


# ---------------------------------------------------------------------------
# Real-world OSRM routing (geocoding + drive-time calculation)
# ---------------------------------------------------------------------------

def _geocode_census(addr: str) -> tuple[float, float] | None:
    """Geocode a US address using the Census Bureau's free geocoder.

    Handles structured US addresses (street, city, state, zip) that
    Nominatim often fails on. No API key, no rate limit.

    Returns (lat, lon) or None.
    """
    import json
    import urllib.request
    import urllib.parse

    # Parse address components from the input string.
    parts = [p.strip() for p in addr.split(",")]
    if len(parts) < 2:
        return None

    street = parts[0]
    zip_match = re.search(r'\b(\d{5}(?:-\d{4})?)\b', parts[-1])
    zip_code = zip_match.group(1) if zip_match else ""
    has_street_number = bool(re.search(r'\d', parts[0]))
    if not has_street_number and not zip_code:
        return None
    state, _remainder_state = _extract_state(parts[-1])
    if len(parts) >= 3:
        city = parts[-2].strip()
    elif len(parts) == 2 and state:
        if re.search(r'\d', parts[0]):
            remainder = re.sub(r'\b\d{5}(?:-\d{4})?\b', '', parts[1])
            remainder = re.sub(r'\b[A-Za-z]{2}\b', '', remainder)
            city = remainder.strip().rstrip(",").strip()
        else:
            city = parts[0].strip()
            street = ""
    else:
        city = ""

    if not city or not state:
        return None
    has_street = bool(re.search(r'\d', street))
    if has_street and not zip_code:
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

    When the origin geocodes to the continental US and the destination
    lacks state/country qualification (no comma), appends ``, USA`` to
    the destination query to prevent ambiguous city names like
    *Portland*, *Springfield*, or *St. Petersburg* from resolving to
    their more-famous international counterparts.

    Returns None when geocoding or routing fails.
    """
    import urllib.request
    import urllib.parse
    import json
    import time

    # ── Step 1a: Geocode origin to determine country context ────────────
    origin_coord = _geocode_census(origin)
    if not origin_coord:
        time.sleep(1.2)
        origin_coord = _geocode_nominatim(origin)
    if not origin_coord:
        logger.warning("All geocoders failed for origin %r", origin[:60])
        return None

    # ── Step 1b: Bias destination toward US when appropriate ────────────
    origin_lat, origin_lon = origin_coord
    in_us = 24.0 <= origin_lat <= 49.5 and -125.0 <= origin_lon <= -66.0

    dest_query = destination
    if in_us and "," not in destination:
        # Destination is an unqualified city name — append country context
        # so Nominatim resolves "Portland" → Portland, OR (not UK),
        # "St. Petersburg" → Florida (not Russia), etc.
        dest_query = f"{destination}, USA"

    # ── Step 1c: Geocode destination (with bias, falling back without) ──
    dest_coord = _geocode_census(dest_query)
    if not dest_coord:
        time.sleep(1.2)
        dest_coord = _geocode_nominatim(dest_query)
    if not dest_coord and dest_query != destination:
        # Retry without US bias in case the city genuinely isn't in the US
        time.sleep(1.2)
        dest_coord = _geocode_nominatim(destination)
    if not dest_coord:
        logger.warning("All geocoders failed for destination %r", destination[:60])
        return None

    lat1, lon1 = origin_coord
    lat2, lon2 = dest_coord

    # ── Step 2: Real routing via OSRM public API ───────────────────────
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


def _extract_state(text: str) -> tuple[str, str]:
    """Extract a US state from text, returning (code, remainder_without_state)."""
    # Minimal state extraction for geocoding — delegates to the full
    # implementation in search.py when available, otherwise uses a basic
    # 2-letter code regex.
    state_match = re.search(
        r'\b(A[LKZR]|C[AOT]|D[EC]|F[LM]|G[AU]|HI|I[DLNA]|K[SY]|LA'
        r'|M[ADEHINOPST]|N[CDEHJMVY]|O[HKR]|P[AWR]|RI|S[CD]|T[NX]|UT'
        r'|V[AIT]|W[AIVY])\b',
        text,
    )
    if state_match:
        code = state_match.group(1).upper()
        remainder = re.sub(
            r'\b' + state_match.group(1) + r'\b', '', text, count=1, flags=re.IGNORECASE,
        )
        return (code, remainder.strip())
    return ("", text)
