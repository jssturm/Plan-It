"""Shared US state name/code mappings used across the engine package.

Previously duplicated in ``search.py`` and ``db.py``.  A single source of
truth avoids drift and reduces maintenance burden.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Full name → 2-letter code
# ---------------------------------------------------------------------------
US_STATE_NAMES: dict[str, str] = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY",
    # District / territories commonly appearing in US addresses
    "district of columbia": "DC", "washington dc": "DC", "dc": "DC",
    "puerto rico": "PR", "guam": "GU", "us virgin islands": "VI",
}

# ---------------------------------------------------------------------------
# Reverse mapping: 2-letter code → full name
# ---------------------------------------------------------------------------
CODE_TO_NAME: dict[str, str] = {
    code: name.title() for name, code in US_STATE_NAMES.items()
}

# Regex that matches any US state abbreviation (2 letters)
STATE_PATTERN_2LETTER = (
    r"\b(A[LKZR]|C[AOT]|D[EC]|F[LM]|G[AU]|HI|I[DLNA]|K[SY]|LA"
    r"|M[ADEHINOPST]|N[CDEHJMVY]|O[HKR]|P[AWR]|RI|S[CD]|T[NX]|UT"
    r"|V[AIT]|W[AIVY])\b"
)


def resolve_state_code(raw: str) -> str:
    """Convert a state identifier (2-letter code or full name) to a 2-letter code.

    Returns the uppercased input if no match — but always handles the
    common case of "Florida" → "FL".
    """
    if not raw:
        return ""
    stripped = raw.strip()
    upper = stripped.upper()
    # Already a 2-letter code
    if len(upper) == 2 and upper in {v for v in US_STATE_NAMES.values()}:
        return upper
    # Try full name match
    lower = stripped.lower()
    code = US_STATE_NAMES.get(lower)
    if code:
        return code
    # Partial fallback
    for name, code_val in US_STATE_NAMES.items():
        if lower in name or name in lower:
            return code_val
    return upper
