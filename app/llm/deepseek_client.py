"""DeepSeek LLM client — structured travel intent extraction.

Uses the DeepSeek API (OpenAI-compatible chat completions) to parse
free-text trip descriptions into structured intent dicts.  Falls back
to the deterministic regex parser on API failure or when no key is set.

Environment:
    DEEPSEEK_API_KEY — API key for api.deepseek.com (free tier available)
    DEEPSEEK_MODEL   — model name (default: deepseek-chat)
"""

from __future__ import annotations

import json
import logging
import os
import urllib.request
from functools import lru_cache
from typing import Any

logger = logging.getLogger("plan-it.llm")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
_API_URL = "https://api.deepseek.com/v1/chat/completions"
_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# ---------------------------------------------------------------------------
# Low-level API call
# ---------------------------------------------------------------------------

def call_deepseek(prompt: str, system: str = "", temperature: float = 0.3) -> str:
    """Call the DeepSeek chat completions API.

    Args:
        prompt: User message content.
        system: Optional system message (instruction context).
        temperature: Sampling temperature (0.0–2.0, lower = more deterministic).

    Returns:
        The assistant's response text.

    Raises:
        RuntimeError: If DEEPSEEK_API_KEY is not set.
        OSError: On network or HTTP errors.
    """
    if not _API_KEY:
        raise RuntimeError(
            "DEEPSEEK_API_KEY environment variable is not set. "
            "Get a free key at https://platform.deepseek.com/"
        )

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = json.dumps({
        "model": _MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 800,
    }).encode("utf-8")

    req = urllib.request.Request(
        _API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_API_KEY}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode() if exc.fp else str(exc)
        logger.error("DeepSeek API HTTP %d: %s", exc.code, error_body[:300])
        raise
    except Exception:
        logger.exception("DeepSeek API request failed")
        raise

    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("DeepSeek returned no choices")

    content = choices[0].get("message", {}).get("content", "")
    logger.info("DeepSeek response: %d chars", len(content))
    return content


# ---------------------------------------------------------------------------
# Travel intent extraction
# ---------------------------------------------------------------------------

_TRAVEL_SYSTEM_PROMPT = """You are a travel intent parser. Extract structured trip information from free-text descriptions.

Return ONLY valid JSON (no markdown, no explanation) with these fields:
{
  "venue": "primary destination name",
  "location": "city or region of the venue (empty string if unknown)",
  "time_of_day": "morning|afternoon|evening",
  "date_hint": "tomorrow|today|next week|next month|this weekend|empty string",
  "starting_location": "departure point if mentioned (empty string if not)",
  "restaurant_preferences": "dietary/cuisine preferences if mentioned (empty string if not)",
  "is_multiday": true/false,
  "trip_type": "theme_park|museum|city_tour|road_trip|beach|hiking|general",
  "special_requests": ["any special needs or requests mentioned"],
  "confidence": 0.0-1.0
}

Rules:
- venue: extract the MAIN destination. If multiple destinations, pick the primary one.
- location: extract city/region. "Orlando" from "Disney World in Orlando". 
- time_of_day: infer from words like "morning", "afternoon", "evening", "breakfast", "lunch", "dinner", "sunrise", "night". Default "morning".
- date_hint: extract from "tomorrow", "next Saturday", "this weekend", etc.
- starting_location: extract from "from X", "leaving from X", "departing X".
- is_multiday: true if user mentions hotel, overnight, "next day", "drive back", "stay the night".
- trip_type: classify the kind of trip.
- special_requests: list any specific asks (vegetarian food, wheelchair accessible, budget-friendly, etc.)
- confidence: your confidence in the extraction (0.0-1.0). Use 0.5 for ambiguous inputs."""


def parse_travel_intent(user_input: str) -> dict[str, Any]:
    """Parse free-text trip description into structured intent using DeepSeek.

    Falls back to the deterministic regex parser on any failure.

    Args:
        user_input: Raw user text describing the trip.

    Returns:
        Dict matching the intent schema used by the planner (venue, location,
        time_of_day, starting_location, plus LLM-specific fields).
    """
    try:
        response = call_deepseek(user_input, system=_TRAVEL_SYSTEM_PROMPT, temperature=0.1)
        # DeepSeek may wrap JSON in ```json ... ``` blocks
        response = response.strip()
        if response.startswith("```"):
            # Strip markdown code fences
            lines = response.split("\n")
            response = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        result = json.loads(response)
        logger.info(
            "LLM intent parsed: venue=%r location=%r confidence=%.2f",
            result.get("venue", "")[:40],
            result.get("location", ""),
            result.get("confidence", 0),
        )
        return result
    except Exception as exc:
        logger.warning("LLM intent parsing failed, falling back to regex: %s", exc)
        return _fallback_intent(user_input)


# ---------------------------------------------------------------------------
# Fallback: deterministic regex parser (mirrors planner._parse_intent)
# ---------------------------------------------------------------------------

_VENUE_INDICATORS = [
    "to ", "at ", "visit ", "trip to ", "plan ", "going to ",
    "travel to ", "head to ", "explore ", "tour ",
]


def _fallback_intent(user_input: str) -> dict[str, Any]:
    """Deterministic fallback when the LLM is unavailable."""
    text = user_input.strip()
    text_lower = text.lower()

    # Extract "from X" pattern
    inferred_start = ""
    for marker in (" from ", " leaving from ", " departing from "):
        if marker in text_lower:
            after_from = text_lower.split(marker, 1)[-1]
            candidate = (
                after_from.split(",")[0]
                .split(" tomorrow")[0]
                .split(" today")[0]
                .split(" with")[0]
                .split(" and ")[0]
                .split(" to ")[0]
                .strip()
            )
            if candidate and len(candidate) > 2:
                inferred_start = candidate.title()
            break

    # Extract venue
    venue = text
    for indicator in _VENUE_INDICATORS:
        if indicator in text_lower:
            after = text.split(indicator, 1)[-1].strip()
            venue = (
                after.split(",")[0]
                .split(" tomorrow")[0]
                .split(" today")[0]
                .split(" this")[0]
                .split(" with")[0]
                .split(" from ")[0]
                .split(" and ")[0]
                .strip()
            )
            break

    # Time of day
    time_of_day = "morning"
    if any(w in text_lower for w in ("morning", "breakfast", "early", "sunrise", "dawn")):
        time_of_day = "morning"
    elif any(w in text_lower for w in ("afternoon", "noon", "lunch")):
        time_of_day = "afternoon"
    elif any(w in text_lower for w in ("evening", "dinner", "night")):
        time_of_day = "evening"

    # Multi-day detection
    multiday_keywords = [
        "hotel", "stay overnight", "overnight", "next day",
        "drive back", "return trip", "spend the night",
    ]
    is_multiday = any(kw in text_lower for kw in multiday_keywords)

    return {
        "venue": venue,
        "location": "",
        "time_of_day": time_of_day,
        "date_hint": "",
        "starting_location": inferred_start,
        "restaurant_preferences": "",
        "is_multiday": is_multiday,
        "trip_type": "general",
        "special_requests": [],
        "confidence": 0.3,
    }


# ---------------------------------------------------------------------------
# Availability check
# ---------------------------------------------------------------------------

@lru_cache
def is_available() -> bool:
    """Return True if the DeepSeek API key is configured."""
    return bool(_API_KEY)
