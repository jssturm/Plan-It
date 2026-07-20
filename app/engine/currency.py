"""Currency conversion — free exchangerate-api.com, no API key required.

Provides real-time exchange rates for displaying prices in the user's
local currency.  Especially useful for international travelers.

API: https://api.exchangerate-api.com/v4/latest/USD (free, no key)
"""

from __future__ import annotations

import json
import logging
import urllib.request
from functools import lru_cache
from typing import Any

logger = logging.getLogger("plan-it.currency")

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_rates() -> dict[str, float] | None:
    """Fetch latest exchange rates (base USD).  Cached for the process lifetime."""
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Plan-It/0.3"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            rates = data.get("rates", {})
            logger.info("Exchange rates loaded: %d currencies", len(rates))
            return rates
    except Exception as exc:
        logger.warning("Currency rates unavailable: %s", exc)
        return None


def get_rate(currency_code: str) -> float | None:
    """Get the exchange rate for a currency code (e.g. 'EUR', 'BRL', 'GBP').

    Returns the rate (1 USD = X units), or None if unavailable.
    """
    rates = _get_rates()
    if rates is None:
        return None
    return rates.get(currency_code.upper())


def convert_usd(amount_usd: float, to_currency: str) -> tuple[float, str] | None:
    """Convert a USD amount to another currency.

    Returns (converted_amount, currency_symbol) or None.
    """
    rate = get_rate(to_currency)
    if rate is None:
        return None
    converted = round(amount_usd * rate, 2)
    symbol = _currency_symbol(to_currency)
    return (converted, symbol)


def detect_user_currency() -> str:
    """Heuristic: guess the user's currency from common patterns.

    Returns an ISO 4217 currency code (default 'USD').
    """
    # For now, return USD. In production this could use:
    # - Accept-Language header parsing
    # - IP geolocation
    # - User preference
    return "USD"


def format_price(usd_price: str, target_currency: str = "") -> str:
    """Convert a USD price string like '$45-65/day' to the target currency.

    If target_currency is empty or 'USD', returns the original string.
    """
    if not target_currency or target_currency.upper() == "USD":
        return usd_price

    import re

    # Extract dollar amounts from the price string
    def convert_match(m):
        amount = float(m.group(1))
        result = convert_usd(amount, target_currency)
        if result is None:
            return m.group(0)
        converted, symbol = result
        if converted == int(converted):
            return f"{symbol}{int(converted)}"
        return f"{symbol}{converted:.2f}"

    # Replace $XX patterns
    converted = re.sub(r'\$(\d+(?:\.\d+)?)', convert_match, usd_price)
    return converted


def _currency_symbol(code: str) -> str:
    """Map ISO 4217 code to a currency symbol."""
    symbols: dict[str, str] = {
        "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥",
        "BRL": "R$", "CAD": "C$", "AUD": "A$", "MXN": "MX$",
        "CNY": "¥", "INR": "₹", "KRW": "₩", "CHF": "Fr",
        "SEK": "kr", "NOK": "kr", "DKK": "kr", "PLN": "zł",
        "RUB": "₽", "TRY": "₺", "ZAR": "R", "NGN": "₦",
    }
    return symbols.get(code.upper(), f"{code} ")
