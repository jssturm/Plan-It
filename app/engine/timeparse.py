"""Shared free-form time parsing used by planner, calendar, and API schemas.

Normalizes user-entered times to canonical ``HH:MM AM/PM`` (with optional
`` +N`` day offset from ``fmt_time`` overflow handling).
"""

from __future__ import annotations

import re


def to_24h(hour: int, meridiem: str | None) -> int | None:
    """Convert hour + optional AM/PM to 24-hour clock, or None if invalid."""
    if meridiem:
        if hour < 1 or hour > 12:
            return None
        if meridiem == "AM" and hour == 12:
            return 0
        if meridiem == "PM" and hour != 12:
            return hour + 12
        return hour
    if hour < 0 or hour > 23:
        return None
    return hour


def fmt_time(hour: int, minute: int) -> str:
    """Format a 24-hour hour and minute as a 12-hour clock string.

    Handles overflow beyond 24 hours by appending a `` +N`` day-offset
    suffix (e.g. ``02:48 AM +1`` for hour=26).
    """
    day_offset = hour // 24
    hour = hour % 24
    meridiem = "AM"
    if hour >= 12:
        meridiem = "PM"
    display_h = hour if hour <= 12 else hour - 12
    if display_h == 0:
        display_h = 12
    suffix = f" +{day_offset}" if day_offset > 0 else ""
    return f"{display_h:02d}:{minute:02d} {meridiem}{suffix}"


def normalize_time(raw: str) -> str:
    """Normalize a user-entered time string to ``HH:MM AM/PM`` format.

    Accepts ``7:00 AM``, ``07:00``, ``7am``, ``0700``, ``0800 AM``,
    ``7:00AM``, bare hour integers, and similar free-form variants.
    Returns the normalized time string or the raw input if unparseable.
    """
    if raw is None:
        return raw
    stripped = re.sub(r"[.\u00b7]", ":", str(raw).strip().upper())
    stripped = re.sub(r"\s+", " ", stripped).strip()
    # Drop day-offset suffixes for parsing; re-apply via fmt when needed.
    extra_hours = 0
    day_m = re.search(r"\s*\+(\d+)\s*$", stripped)
    if day_m:
        extra_hours = 24 * int(day_m.group(1))
        stripped = stripped[: day_m.start()].strip()

    def _finish(hour: int, minute: int, meridiem: str | None) -> str | None:
        if minute < 0 or minute > 59:
            return None
        hour_24 = to_24h(hour, meridiem)
        if hour_24 is None:
            return None
        return fmt_time(hour_24 + extra_hours, minute)

    m = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)?$", stripped)
    if m:
        result = _finish(int(m.group(1)), int(m.group(2)), m.group(3))
        if result:
            return result

    m = re.match(r"^(\d{3,4})\s*(AM|PM)?$", stripped)
    if m:
        digits = m.group(1)
        meridiem = m.group(2)
        if len(digits) == 3:
            hour, minute = int(digits[0]), int(digits[1:])
        else:
            hour, minute = int(digits[:2]), int(digits[2:])
        result = _finish(hour, minute, meridiem)
        if result:
            return result

    m = re.match(r"^(\d{1,2})\s*(AM|PM)$", stripped)
    if m:
        result = _finish(int(m.group(1)), 0, m.group(2))
        if result:
            return result

    m = re.match(r"^(\d{1,2})$", stripped)
    if m:
        result = _finish(int(m.group(1)), 0, None)
        if result:
            return result

    return str(raw)


def parse_time(time_str: str, *, default: tuple[int, int] = (8, 0)) -> tuple[int, int]:
    """Parse a free-form time to ``(hour_24, minute)``.

    Uses :func:`normalize_time` first so compact forms like ``0800 AM`` work.
    Falls back to *default* when unparseable.
    """
    if not time_str or not str(time_str).strip():
        return default

    normalized = normalize_time(time_str)
    m = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)", normalized, re.IGNORECASE)
    if not m:
        return default

    h = int(m.group(1))
    minute = int(m.group(2))
    meridiem = m.group(3).upper()
    hour_24 = to_24h(h, meridiem)
    if hour_24 is None:
        return default
    return (hour_24, minute)


# Back-compat aliases used throughout the planner
_fmt_time = fmt_time
_normalize_departure_time = normalize_time
_parse_time = parse_time
