"""Weather forecast integration — free Open-Meteo API, no API key required.

Provides current conditions, daily forecasts, and hourly precipitation
data for any geographic location.  Integrates with the planner to add
weather-aware notes (packing suggestions, rain contingency, temperature
context) to generated itineraries.

API: https://open-meteo.com/  (free, no key, no rate limit beyond fair use)
"""

from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import Any

logger = logging.getLogger("plan-it.weather")

# Vercel serverless has a 10-second function timeout on Hobby plans.
# Weather lookups must complete well under that budget or risk 504s.
_GEOCODE_TIMEOUT_S = 3
_FORECAST_TIMEOUT_S = 5

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@lru_cache(maxsize=64)
def get_forecast(lat: float, lon: float, target_date: str = "") -> dict[str, Any] | None:
    """Fetch a weather forecast for a location.

    Args:
        lat: Latitude.
        lon: Longitude.
        target_date: ISO date string (YYYY-MM-DD).  Defaults to today.

    Returns:
        Dict with keys: temperature_max, temperature_min, conditions,
        precipitation_probability, wind_speed, alerts, packing_suggestions.
        Returns None on failure.
    """
    if not target_date:
        target_date = date.today().isoformat()

    # Open-Meteo forecast API — free, no key
    params = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "weathercode",
            "wind_speed_10m_max",
        ],
        "timezone": "auto",
        "forecast_days": 7,
    }, doseq=True)

    url = f"https://api.open-meteo.com/v1/forecast?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Plan-It/0.3"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
    except Exception as exc:
        logger.warning("Open-Meteo forecast failed for (%.4f, %.4f): %s", lat, lon, exc)
        return None

    daily = data.get("daily", {})
    if not daily:
        return None

    # Find the target date in the response
    dates = daily.get("time", [])
    try:
        day_idx = dates.index(target_date)
    except ValueError:
        # Target date not in forecast range — use the closest day
        day_idx = 0

    if day_idx >= len(dates):
        day_idx = len(dates) - 1

    temp_max = _get(daily, "temperature_2m_max", day_idx)
    temp_min = _get(daily, "temperature_2m_min", day_idx)
    precip_prob = _get(daily, "precipitation_probability_max", day_idx)
    weather_code = _get(daily, "weathercode", day_idx)
    wind_speed = _get(daily, "wind_speed_10m_max", day_idx)

    conditions = _weather_code_to_text(weather_code)
    alerts = _build_alerts(conditions, precip_prob, wind_speed, temp_max)
    packing = _build_packing_suggestions(temp_max, temp_min, precip_prob, conditions)

    forecast = {
        "temperature_max": temp_max,
        "temperature_min": temp_min,
        "temperature_unit": "°F",
        "conditions": conditions,
        "precipitation_probability": precip_prob,
        "wind_speed_max": wind_speed,
        "alerts": alerts,
        "packing_suggestions": packing,
    }

    logger.info(
        "Weather for (%.2f, %.2f) on %s: %s, %s–%s°F, precip %s%%",
        lat, lon, target_date, conditions, temp_min, temp_max, precip_prob,
    )
    return forecast


def get_forecast_for_location(
    location_name: str, target_date: str = ""
) -> dict[str, Any] | None:
    """Convenience wrapper: geocode a location name then fetch its forecast.

    Uses Nominatim for geocoding (free, no key).
    """
    lat, lon = _geocode_location(location_name)
    if lat is None:
        return None
    return get_forecast(lat, lon, target_date)


def weather_summary_for_plan(
    venue_name: str, venue_location: str = ""
) -> dict[str, Any] | None:
    """Get a concise weather summary suitable for injecting into a travel plan.

    Returns a dict with ``note`` (one-line summary) and ``packing`` (list)
    ready to append to strategy_notes / alerts, or None if unavailable.
    """
    search_loc = f"{venue_name} {venue_location}".strip()
    forecast = get_forecast_for_location(search_loc)
    if forecast is None:
        return None

    temp = f"{forecast['temperature_min']}–{forecast['temperature_max']}°F"
    note = (
        f"Weather: {forecast['conditions']}, {temp}, "
        f"{forecast['precipitation_probability']}% chance of rain"
    )

    return {
        "note": note,
        "packing": forecast["packing_suggestions"],
        "alerts": forecast["alerts"],
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _geocode_location(name: str) -> tuple[float | None, float | None]:
    """Geocode a location name to lat/lon using Nominatim."""
    params = urllib.parse.urlencode({"q": name, "format": "json", "limit": 1})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Plan-It/0.3"})
        with urllib.request.urlopen(req, timeout=_GEOCODE_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode())
            if data:
                return (float(data[0]["lat"]), float(data[0]["lon"]))
    except Exception:
        pass
    return (None, None)


def _get(data: dict, key: str, idx: int) -> Any:
    """Safely index into a list-valued dict key."""
    values = data.get(key, [])
    if idx < len(values):
        return values[idx]
    return None


# WMO weather code → human-readable description
# https://open-meteo.com/en/docs#weathervariables
_WMO_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _weather_code_to_text(code: int | None) -> str:
    if code is None:
        return "Unknown"
    return _WMO_CODES.get(int(code), f"Code {code}")


def _build_alerts(
    conditions: str, precip_prob: int | None, wind_speed: float | None, temp_max: float | None
) -> list[str]:
    """Build a list of weather alert strings."""
    alerts: list[str] = []
    conditions_lower = conditions.lower()

    if precip_prob is not None and precip_prob > 50:
        if "rain" in conditions_lower or "drizzle" in conditions_lower:
            alerts.append(f"⚠ {precip_prob}% chance of rain — pack an umbrella or waterproof jacket")
        elif "snow" in conditions_lower:
            alerts.append(f"⚠ {precip_prob}% chance of snow — check road conditions before departing")
        elif "thunderstorm" in conditions_lower:
            alerts.append(f"⚠ {precip_prob}% chance of thunderstorms — outdoor attractions may close temporarily")

    if temp_max is not None:
        if temp_max > 95:
            alerts.append("🌡 Extreme heat expected — bring extra water, sunscreen, and take shade breaks")
        elif temp_max > 88:
            alerts.append("🌡 Hot day ahead — stay hydrated and use sunscreen")
        elif temp_max < 45:
            alerts.append("🥶 Cold temperatures — dress in layers and bring gloves")

    if wind_speed is not None and wind_speed > 25:
        alerts.append("💨 Strong winds forecast — secure loose items and expect ride closures at theme parks")

    return alerts


def _build_packing_suggestions(
    temp_max: float | None,
    temp_min: float | None,
    precip_prob: int | None,
    conditions: str,
) -> list[str]:
    """Build packing suggestion strings."""
    suggestions: list[str] = []
    conditions_lower = conditions.lower()

    if precip_prob is not None and precip_prob > 30:
        suggestions.append("☂ Umbrella or rain jacket")
    if temp_max is not None and temp_max > 80:
        suggestions.append("🧴 Sunscreen")
        suggestions.append("🕶 Sunglasses")
        suggestions.append("💧 Refillable water bottle")
    if temp_min is not None and temp_min < 50:
        suggestions.append("🧥 Warm layer / jacket")
    if temp_max is not None and temp_max > 60 and "rain" not in conditions_lower:
        suggestions.append("👟 Comfortable walking shoes")

    if not suggestions:
        suggestions.append("👟 Comfortable walking shoes")

    return suggestions
