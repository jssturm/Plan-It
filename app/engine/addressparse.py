"""Graceful US address parsing for free-form starting locations.

Accepts comma-separated or run-on addresses and extracts street / city /
state / ZIP so Census geocoding can succeed without forcing users into a
single punctuation style.
"""

from __future__ import annotations

import re
from typing import TypedDict

from app.engine.states import STATE_PATTERN_2LETTER, US_STATE_NAMES

_STREET_SUFFIX = (
    r"(?:street|st|avenue|ave|boulevard|blvd|road|rd|drive|dr|lane|ln|"
    r"court|ct|circle|cir|way|place|pl|terrace|ter|parkway|pkwy|"
    r"highway|hwy|trail|trl|pike)\.?"
)

_ZIP_RE = re.compile(r"\b(\d{5}(?:-\d{4})?)\b")


class AddressParts(TypedDict):
    street: str
    city: str
    state: str
    zip: str
    formatted: str


def _extract_state(text: str) -> tuple[str, str]:
    """Return (state_code, remainder_without_state)."""
    best_len = 0
    best_code = ""
    text_lower = text.lower()
    for name, code in sorted(US_STATE_NAMES.items(), key=lambda x: -len(x[0])):
        # Require word boundaries for short names like "dc"
        pattern = r"\b" + re.escape(name) + r"\b"
        if re.search(pattern, text_lower) and len(name) > best_len:
            best_len = len(name)
            best_code = code

    if best_code:
        for full_name, code in US_STATE_NAMES.items():
            if code == best_code and len(full_name) == best_len:
                remainder = re.sub(
                    r"\b" + re.escape(full_name) + r"\b",
                    "",
                    text,
                    count=1,
                    flags=re.IGNORECASE,
                )
                return best_code, re.sub(r"\s{2,}", " ", remainder).strip(" ,")
        return best_code, text

    state_match = re.search(STATE_PATTERN_2LETTER, text, flags=re.IGNORECASE)
    if state_match:
        code = state_match.group(1).upper()
        remainder = re.sub(
            r"\b" + re.escape(state_match.group(1)) + r"\b",
            "",
            text,
            count=1,
            flags=re.IGNORECASE,
        )
        return code, re.sub(r"\s{2,}", " ", remainder).strip(" ,")
    return "", text


def _split_street_city(remainder: str) -> tuple[str, str]:
    """Split leftover text into (street, city) when possible."""
    remainder = remainder.strip(" ,")
    if not remainder:
        return "", ""

    # Street number + street name ending in a known suffix, then city
    m = re.match(
        rf"^(\d+\s+.{{1,80}}?\b{_STREET_SUFFIX})\s+(.+)$",
        remainder,
        flags=re.IGNORECASE,
    )
    if m:
        return m.group(1).strip(" ,"), m.group(2).strip(" ,")

    # Leading street number without recognized suffix: last token(s) = city
    if re.match(r"^\d+", remainder):
        tokens = remainder.split()
        if len(tokens) >= 3:
            # Prefer last 1 token as city; if last is short directional, take 2
            if len(tokens) >= 4 and tokens[-1].lower() in {"n", "s", "e", "w", "ne", "nw", "se", "sw"}:
                return " ".join(tokens[:-2]), " ".join(tokens[-2:])
            return " ".join(tokens[:-1]), tokens[-1]
        if len(tokens) == 2:
            return tokens[0], tokens[1]

    # No street number — treat whole remainder as city / place name
    return "", remainder


def parse_us_address(raw: str) -> AddressParts:
    """Extract street, city, state, ZIP from free-form or structured input."""
    empty: AddressParts = {
        "street": "",
        "city": "",
        "state": "",
        "zip": "",
        "formatted": (raw or "").strip(),
    }
    if not raw or not str(raw).strip():
        return empty

    text = re.sub(r"\s+", " ", str(raw).strip())
    text = text.replace(";", ",")

    zip_code = ""
    zip_m = _ZIP_RE.search(text)
    if zip_m:
        zip_code = zip_m.group(1)
        text = (text[: zip_m.start()] + " " + text[zip_m.end() :]).strip(" ,")

    state, remainder = _extract_state(text)
    remainder = remainder.strip(" ,")

    street = ""
    city = ""

    if "," in remainder:
        parts = [p.strip() for p in remainder.split(",") if p.strip()]
        if len(parts) >= 2:
            # Heuristic: first part is street if it has a digit; else place,city
            if re.search(r"\d", parts[0]):
                street = parts[0]
                city = parts[-1]
                if len(parts) > 2 and not city:
                    city = parts[1]
            else:
                city = parts[-1]
                street = ", ".join(parts[:-1]) if len(parts) > 1 else ""
                if not re.search(r"\d", street):
                    # "Downtown, Orlando" style — keep last as city, drop street
                    city = parts[-1]
                    street = ""
        elif len(parts) == 1:
            street, city = _split_street_city(parts[0])
    else:
        street, city = _split_street_city(remainder)

    # If state extraction ate everything and we only have zip, bail gracefully
    formatted = format_address(street, city, state, zip_code) or str(raw).strip()
    return {
        "street": street,
        "city": city,
        "state": state,
        "zip": zip_code,
        "formatted": formatted,
    }


def format_address(street: str, city: str, state: str, zip_code: str) -> str:
    """Build a canonical ``street, city, ST ZIP`` string from parts."""
    chunks: list[str] = []
    if street:
        chunks.append(street.strip())
    city_state = " ".join(x for x in [city.strip(), state.strip()] if x).strip()
    if zip_code:
        city_state = f"{city_state} {zip_code}".strip() if city_state else zip_code
    if city_state:
        chunks.append(city_state)
    return ", ".join(chunks)


def normalize_us_address(raw: str) -> str:
    """Return a comma-structured address when components can be inferred.

    Unparseable input is returned stripped unchanged (never raises).
    """
    if not raw or not str(raw).strip():
        return raw
    parts = parse_us_address(raw)
    # Only rewrite when we confidently found state or zip — otherwise keep raw
    # so hotel/landmark names are not mangled.
    if parts["state"] or parts["zip"]:
        return parts["formatted"]
    return str(raw).strip()
