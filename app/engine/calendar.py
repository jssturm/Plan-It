"""iCalendar (.ics) export — generates downloadable calendar files from travel plans.

Produces RFC 5545-compliant iCalendar data that users can import into
Google Calendar, Apple Calendar, Outlook, or any standards-compliant
calendar application.  Each schedule item becomes a timed event with
location (maps URL) and description (action text).
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger("plan-it.calendar")

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_icalendar(plan: dict, plan_id: str = "") -> str:
    """Build an RFC 5545 iCalendar string from a Plan-It travel plan.

    Uses the ``icalendar`` library when available for standards-compliant
    output.  Falls back to raw iCalendar text generation if the library
    is not installed.

    Args:
        plan: The full plan dict (must have ``schedule`` and ``route`` keys).
        plan_id: Optional plan identifier used as the calendar UID suffix.

    Returns:
        A complete iCalendar string (``text/calendar`` MIME type).
    """
    try:
        from icalendar import Alarm, Calendar, Event  # noqa: F811
        return _generate_with_icalendar(plan, plan_id, Calendar, Event, Alarm)
    except ImportError:
        logger.warning("icalendar library not available, using raw iCalendar output")
        return _generate_raw(plan, plan_id)


def _generate_with_icalendar(
    plan: dict, plan_id: str, Calendar, Event, Alarm
) -> str:
    """Generate iCalendar using the icalendar library."""
    cal = Calendar()
    cal.add("prodid", "-//Plan-It//Travel Itinerary//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", "Plan-It Travel Itinerary")

    venue = plan.get("venue_type", "Trip")
    schedule = plan.get("schedule", [])
    route = plan.get("route", [])

    if not schedule:
        return cal.to_ical().decode("utf-8")

    # Use the trip_date if available, otherwise pick a sensible default
    trip_date_str = plan.get("trip_date", "")
    if trip_date_str:
        try:
            event_date = datetime.fromisoformat(trip_date_str)
        except (ValueError, TypeError):
            event_date = _pick_event_date(plan)
    else:
        event_date = _pick_event_date(plan)

    for idx, item in enumerate(schedule):
        time_str = item.get("time", "").strip()
        start_dt = _parse_to_datetime(time_str, event_date)
        if start_dt is None:
            continue

        walk = item.get("walking_time_min") or 0
        wait = item.get("wait_time_min") or 0
        duration_min = max(walk + wait + 10, 30)
        end_dt = start_dt + timedelta(minutes=duration_min)

        uid = f"planit-{plan_id[:8] if plan_id else 'trip'}-{idx}@plan-it.app"

        event = Event()
        event.add("uid", uid)
        event.add("dtstart", start_dt)
        event.add("dtend", end_dt)
        event.add("summary", item.get("action", "Plan-It stop"))

        desc_parts = [item.get("action", "")]
        if item.get("restaurant"):
            desc_parts.append(f"Restaurant: {item['restaurant']}")
        if item.get("meal_timing_note"):
            desc_parts.append(f"Tip: {item['meal_timing_note']}")
        if item.get("backup_plan"):
            desc_parts.append(f"Backup: {item['backup_plan']}")
        event.add("description", "\n\n".join(desc_parts))

        location = item.get("walking_map_url") or (route[0].get("maps_url", "") if route else "")
        if location:
            event.add("location", location)

        prio_map = {"high": 1, "medium": 5, "low": 9}
        event.add("priority", prio_map.get(item.get("priority", "medium"), 5))

        reminder_min = item.get("reminder_min")
        if reminder_min and isinstance(reminder_min, (int, float)) and reminder_min > 0:
            alarm = Alarm()
            alarm.add("action", "DISPLAY")
            alarm.add("trigger", timedelta(minutes=-int(reminder_min)))
            alarm.add("description", f"Reminder: {item.get('action', 'Plan-It stop')}")
            event.add_component(alarm)

        cal.add_component(event)

    return cal.to_ical().decode("utf-8")


def _generate_raw(plan: dict, plan_id: str = "") -> str:
    """Fallback: generate RFC 5545 iCalendar text without external libraries."""
    lines: list[str] = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Plan-It//Travel Itinerary//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Plan-It Travel Itinerary",
    ]

    schedule = plan.get("schedule", [])
    route = plan.get("route", [])

    if not schedule:
        lines.append("END:VCALENDAR")
        return "\r\n".join(lines) + "\r\n"

    trip_date_str = plan.get("trip_date", "")
    if trip_date_str:
        try:
            event_date = datetime.fromisoformat(trip_date_str)
        except (ValueError, TypeError):
            event_date = _pick_event_date(plan)
    else:
        event_date = _pick_event_date(plan)

    for idx, item in enumerate(schedule):
        time_str = item.get("time", "").strip()
        start_dt = _parse_to_datetime(time_str, event_date)
        if start_dt is None:
            continue

        walk = item.get("walking_time_min") or 0
        wait = item.get("wait_time_min") or 0
        duration_min = max(walk + wait + 10, 30)
        end_dt = start_dt + timedelta(minutes=duration_min)

        uid = f"planit-{plan_id[:8] if plan_id else 'trip'}-{idx}@plan-it.app"
        summary = item.get("action", "Plan-It stop")
        desc_parts = [item.get("action", "")]
        if item.get("restaurant"):
            desc_parts.append(f"Restaurant: {item['restaurant']}")
        if item.get("meal_timing_note"):
            desc_parts.append(f"Tip: {item['meal_timing_note']}")
        if item.get("backup_plan"):
            desc_parts.append(f"Backup: {item['backup_plan']}")

        location = item.get("walking_map_url") or (route[0].get("maps_url", "") if route else "")

        prio_map = {"high": "1", "medium": "5", "low": "9"}
        priority = prio_map.get(item.get("priority", "medium"), "5")

        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{_sanitize(summary)}",
            f"DESCRIPTION:{_sanitize(chr(92) + 'n' + chr(92) + 'n'.join(desc_parts))}",
        ]
        if location:
            lines.append(f"LOCATION:{_sanitize(location)}")
        lines.append(f"PRIORITY:{priority}")

        reminder_min = item.get("reminder_min")
        if reminder_min and isinstance(reminder_min, (int, float)) and reminder_min > 0:
            lines += [
                "BEGIN:VALARM",
                f"TRIGGER:-PT{int(reminder_min)}M",
                "ACTION:DISPLAY",
                f"DESCRIPTION:Reminder: {_sanitize(summary)}",
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
    """Parse a free-form time string into a datetime on *base_date*."""
    from app.engine.timeparse import normalize_time, parse_time

    time_str = (time_str or "").strip()
    if not time_str:
        return None

    # Handle "+1" / "+N" suffix for next-day events (also preserved by normalize)
    is_next_day = bool(re.search(r"\+\d+", time_str))
    normalized = normalize_time(time_str)
    hour, minute = parse_time(normalized, default=(-1, -1))
    if hour < 0:
        return None

    result = base_date.replace(hour=hour % 24, minute=minute, second=0, microsecond=0)
    # Day offsets beyond +1 from normalize_time's fmt (+N) — apply full offset
    day_m = re.search(r"\+(\d+)", normalized)
    if day_m:
        result += timedelta(days=int(day_m.group(1)))
    elif is_next_day:
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
