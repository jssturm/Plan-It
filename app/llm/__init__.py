"""DeepSeek AI integration for enhanced itinerary planning.

Activated when ``DEEPSEEK_API_KEY`` is set in the environment.
Provides structured prompt generation and response parsing for
DeepSeek models (deepseek-v4-flash, deepseek-reasoner, deepseek-coder).
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("plan-it.llm")

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_enabled() -> bool:
    """Return True when the DeepSeek integration is configured."""
    return bool(os.environ.get("DEEPSEEK_API_KEY"))


def enhance_plan(raw_plan: dict[str, Any], user_input: str) -> dict[str, Any]:
    """Optionally enhance a raw itinerary plan with DeepSeek reasoning.

    When a DeepSeek API key is configured, this sends the current plan
    and user input to the model for enhancements.  When no key is present,
    the raw plan is returned unchanged.

    Args:
        raw_plan: The itinerary dict produced by the deterministic planner.
        user_input: The original natural-language trip description.

    Returns:
        Enhanced (or unchanged) itinerary dict.
    """
    if not is_enabled():
        logger.debug("DeepSeek not configured — returning raw plan")
        return raw_plan

    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
    logger.info("Enhancing plan with DeepSeek model=%s", model)
    # TODO: implement actual DeepSeek API call
    # - construct chat messages with system prompt + user input + raw plan
    # - call DeepSeek API
    # - parse and validate the response
    # - merge enhancements back into the raw plan
    return raw_plan
