"""iCalendar (.ics) export — generates downloadable calendar files from travel plans.

Produces RFC 5545-compliant iCalendar data that users can import into
Google Calendar, Apple Calendar, Outlook, or any standards-compliant
calendar application.  Each schedule item becomes a timed event with
location (maps URL) and description (action text).
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger("plan-it.calendar")

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_icalendar(plan: dict, plan_id: str = "") -> str:
    """Build an RFC 5545 iCalendar string from a Plan-It travel plan.

    Args:
        plan: The full plan dict (must have ``schedule`` and ``route`` keys).
        plan_id: Optional plan identifier used as the calendar UID suffix.

    Returns:
        A complete iCalendar string (``text/calendar`` MIME type).
    """
    lines: list[str] = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Plan-It//Travel Itinerary//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Plan-It Travel Itinerary",
    ]

    venue = plan.get("venue_type", "Trip")
    schedule = plan.get("schedule", [])
    route = plan.get("route", [])

    if not schedule:
        lines.append("END:VCALENDAR")
        return "\r\n".join(lines) + "\r\n"

    # Use today's date as the event date since plans don't carry explicit dates.
    # The departure_time field provides the time-of-day context.
    event_date = _pick_event_date(plan)

    for idx, item in enumerate(schedule):
        time_str = item.get("time", "").strip()
        start_dt = _parse_to_datetime(time_str, event_date)
        if start_dt is None:
            continue

        # Estimate duration: walking + wait time as a rough proxy, minimum 30 min
        walk = item.get("walking_time_min") or 0
        wait = item.get("wait_time_min") or 0
        duration_min = max(walk + wait + 10, 30)
        end_dt = start_dt + timedelta(minutes=duration_min)

        uid = f"planit-{plan_id[:8] if plan_id else 'trip'}-{idx}@plan-it.app"
        summary = _sanitize(item.get("action", "Plan-It stop"))
        description_parts = [item.get("action", "")]
        if item.get("restaurant"):
            description_parts.append(f"Restaurant: {item['restaurant']}")
        if item.get("meal_timing_note"):
            description_parts.append(f"Tip: {item['meal_timing_note']}")
        if item.get("backup_plan"):
            description_parts.append(f"Backup: {item['backup_plan']}")
        description = _sanitize("\\n\\n".join(description_parts))

        location = ""
        if item.get("walking_map_url"):
            location = item["walking_map_url"]
        elif route and len(route) > 0:
            location = route[0].get("maps_url", "")

        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
        ]
        if location:
            lines.append(f"LOCATION:{_sanitize(location)}")

        # Priority: high=1, medium=5, low=9 (RFC 5545 scale)
        prio_map = {"high": "1", "medium": "5", "low": "9"}
        priority = prio_map.get(item.get("priority", "medium"), "5")
        lines.append(f"PRIORITY:{priority}")

        # Reminder alarm if set
        reminder_min = item.get("reminder_min")
        if reminder_min and isinstance(reminder_min, (int, float)) and reminder_min > 0:
            lines += [
                "BEGIN:VALARM",
                f"TRIGGER:-PT{int(reminder_min)}M",
                "ACTION:DISPLAY",
                f"DESCRIPTION:Reminder: {summary}",
                "END:VALARM",
            ]

        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pick_event_date(plan: dict) -> datetime:
    """Pick a reasonable date for calendar events.

    Plans carry ``departure_time`` but not an explicit date.  We use
    today if the departure time hasn't passed yet, otherwise tomorrow,
    so imported events appear on a sensible day in the user's calendar.
    """
    now = datetime.now()
    dep_time = plan.get("departure_time", "").strip()
    if dep_time:
        parsed = _parse_to_datetime(dep_time, now)
        if parsed:
            candidate = now.replace(hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)
            if candidate > now:
                return candidate
    # Default: tomorrow morning
    return (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)


def _parse_to_datetime(time_str: str, base_date: datetime) -> datetime | None:
    """Parse a time string like '07:30 AM' or '08:00 AM +1' into a datetime."""
    import re

    time_str = time_str.strip()
    if not time_str:
        return None

    # Handle "+1" suffix for next-day events
    is_next_day = "+1" in time_str
    time_str = time_str.replace("+1", "").strip()

    m = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)", time_str, re.IGNORECASE)
    if not m:
        return None

    hour = int(m.group(1))
    minute = int(m.group(2))
    meridiem = m.group(3).upper()

    if meridiem == "PM" and hour < 12:
        hour += 12
    if meridiem == "AM" and hour == 12:
        hour = 0

    result = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if is_next_day:
        result += timedelta(days=1)
    return result


def _sanitize(text: str) -> str:
    """Escape special characters for iCalendar text fields."""
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )
