"""SQLite database layer for the tourism knowledge base.

Replaces hardcoded venue/attraction dictionaries with live queries
against the multi-state tourism database (test.db).

Database path is resolved from the project root's data directory
alongside test.db, or from an explicit JEFFOS_DB_PATH env var.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger("plan-it.db")

# ---------------------------------------------------------------------------
# State code normalization — supports both "FL" and "Florida"
# ---------------------------------------------------------------------------
from app.engine.states import resolve_state_code as _resolve_state_code  # noqa: E402

# ---------------------------------------------------------------------------
# Database path resolution
# ---------------------------------------------------------------------------
_DB_PATH: str | None = None


def _resolve_db_path() -> str | None:
    """Find test.db: check JEFFOS_DB_PATH env var, then project root, then development root.

    Returns None when no database file is found (the caller should handle
    graceful degradation to hardcoded venue data).
    """
    global _DB_PATH
    if _DB_PATH is not None:
        return _DB_PATH if _DB_PATH else None

    env_path = os.environ.get("JEFFOS_DB_PATH")
    if env_path and Path(env_path).is_file():
        _DB_PATH = env_path
        return _DB_PATH

    # Project root: check common locations relative to the app package
    candidates = [
        Path(__file__).resolve().parent.parent.parent.parent / "test.db",  # repo root (app/engine/db.py → up 4)
        Path(__file__).resolve().parent.parent.parent / "data" / "test.db",  # repo/data/test.db
        Path(__file__).resolve().parent.parent / "data" / "test.db",  # project/data/test.db (Plan-It layout)
    ]
    for candidate in candidates:
        if candidate.is_file():
            _DB_PATH = str(candidate)
            return _DB_PATH

    logger.warning(
        "test.db not found. Checked: %s. "
        "Set JEFFOS_DB_PATH env var to the full path of test.db. "
        "Database-backed venue lookups will be unavailable; falling back to hardcoded data.",
        [str(c) for c in candidates],
    )
    _DB_PATH = ""  # Sentinel to avoid repeated filesystem checks
    return None


# ---------------------------------------------------------------------------
# Connection management (one shared connection, thread-safe reads)
# ---------------------------------------------------------------------------
_conn: sqlite3.Connection | None = None
_db_unavailable: bool = False


def _get_conn() -> sqlite3.Connection | None:
    global _conn, _db_unavailable
    if _db_unavailable:
        return None
    if _conn is None:
        db_path = _resolve_db_path()
        if db_path is None:
            _db_unavailable = True
            return None
        _conn = sqlite3.connect(db_path)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA foreign_keys=ON")
    return _conn


# ---------------------------------------------------------------------------
# Public API — venue lookups
# ---------------------------------------------------------------------------

@lru_cache(maxsize=256)
def lookup_venue_attractions(venue_name: str, location: str = "", limit: int = 12) -> list[dict[str, Any]]:
    """Return curated attractions for a venue, preferring the database.
    
    Args:
        venue_name: Normalized venue name from the planner (e.g. "Busch Gardens").
        location: Optional city/region to disambiguate (e.g. "Tampa").
        limit: Max number of attractions to return.
        
    Returns:
        List of dicts with keys: name, description, attraction_type, thrill_level, is_signature.
        Returns empty list if venue not found in database.
    """
    conn = _get_conn()
    if conn is None:
        return []
    
    # Try exact match first, then LIKE fallback
    queries = [
        # Exact venue name match, optional location
        ("""SELECT va.name, va.description, va.attraction_type, va.thrill_level,
                   va.is_signature, va.duration_minutes
            FROM venue_attractions va
            JOIN venues v ON va.venue_id = v.id
            JOIN states s ON v.state_id = s.id
            WHERE v.name = ?
            ORDER BY va.is_signature DESC, va.thrill_level
            LIMIT ?""", [venue_name, limit]),
        # LIKE match on venue name
        ("""SELECT va.name, va.description, va.attraction_type, va.thrill_level,
                   va.is_signature, va.duration_minutes
            FROM venue_attractions va
            JOIN venues v ON va.venue_id = v.id
            JOIN states s ON v.state_id = s.id
            WHERE v.name LIKE ?
            ORDER BY va.is_signature DESC, va.thrill_level
            LIMIT ?""", [f"%{venue_name}%", limit]),
    ]
    
    for query, params in queries:
        try:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            if rows:
                return [dict(r) for r in rows]
        except sqlite3.Error as e:
            logger.debug("DB lookup failed for %r: %s", venue_name, e)
    
    return []


@lru_cache(maxsize=256)
def lookup_venue_info(venue_name: str, location: str = "") -> dict[str, Any] | None:
    """Return structured venue metadata from the database.
    
    Args:
        venue_name: Venue name to look up.
        location: Optional city/region for disambiguation.
        
    Returns:
        Dict with venue_type, description, hours, top_attractions, crowd_tips, 
        parking_info, plus state and city metadata. None if not found.
    """
    conn = _get_conn()
    if conn is None:
        return None
    
    queries = [
        ("""SELECT v.name, v.category AS venue_type, v.description, v.city, v.region,
                   s.code AS state_code, s.name AS state_name, v.website, v.parent_company,
                   v.opening_year, v.is_signature
            FROM venues v
            JOIN states s ON v.state_id = s.id
            WHERE v.name = ?
            LIMIT 1""", [venue_name]),
        ("""SELECT v.name, v.category AS venue_type, v.description, v.city, v.region,
                   s.code AS state_code, s.name AS state_name, v.website, v.parent_company,
                   v.opening_year, v.is_signature
            FROM venues v
            JOIN states s ON v.state_id = s.id
            WHERE v.name LIKE ?
            LIMIT 1""", [f"%{venue_name}%"]),
    ]
    
    for query, params in queries:
        try:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            if row:
                venue = dict(row)
                # Add top attractions
                venue["top_attractions"] = [
                    a["name"] for a in lookup_venue_attractions(venue_name, location, limit=8)
                ]
                # Build hours from category defaults
                venue["hours"] = _default_hours(venue.get("venue_type", "general"))
                venue["crowd_tips"] = ["Arrive 30 minutes before opening for shortest lines"]
                venue["parking_info"] = "Parking available on-site"
                venue["alerts"] = []
                return venue
        except sqlite3.Error as e:
            logger.debug("DB venue info lookup failed for %r: %s", venue_name, e)
    
    return None


# ---------------------------------------------------------------------------
# Public API — venue classification
# ---------------------------------------------------------------------------

@lru_cache(maxsize=256)
def classify_venue_from_db(venue_name: str) -> str | None:
    """Return the category of a venue from the database, or None if not found.
    
    This can replace the regex-based _classify_venue() when the DB has a match.
    """
    conn = _get_conn()
    if conn is None:
        return None
    try:
        cursor = conn.execute(
            "SELECT category FROM venues WHERE name LIKE ? LIMIT 1",
            [f"%{venue_name}%"]
        )
        row = cursor.fetchone()
        if row:
            return row[0]
    except sqlite3.Error:
        pass
    return None


# ---------------------------------------------------------------------------
# Public API — state & discovery queries
# ---------------------------------------------------------------------------

@lru_cache(maxsize=32)
def get_state_venues(state_code: str) -> list[dict[str, Any]]:
    """Return all venues for a state, ordered by signature.

    Accepts both 2-letter codes ("FL") and spelled-out names ("Florida").
    """
    code = _resolve_state_code(state_code)
    conn = _get_conn()
    if conn is None:
        return []
    try:
        cursor = conn.execute("""
            SELECT v.name, v.category, v.city, v.region, v.is_signature,
                   v.description, v.website, v.opening_year
            FROM venues v
            JOIN states s ON v.state_id = s.id
            WHERE s.code = ?
            ORDER BY v.is_signature DESC, v.name
        """, [code])
        return [dict(r) for r in cursor.fetchall()]
    except sqlite3.Error:
        return []


@lru_cache(maxsize=32)
def get_state_events(state_code: str, month: int | None = None) -> list[dict[str, Any]]:
    """Return events for a state, optionally filtered by month (1-12).

    Accepts both 2-letter codes ("FL") and spelled-out names ("Florida").
    """
    code = _resolve_state_code(state_code)
    conn = _get_conn()
    if conn is None:
        return []
    try:
        if month:
            cursor = conn.execute("""
                SELECT e.name, e.event_type, e.city, e.month_of_year, e.description,
                       e.annual_attendance, e.is_signature
                FROM state_events e
                JOIN states s ON e.state_id = s.id
                WHERE s.code = ? AND e.month_of_year = ?
                ORDER BY e.is_signature DESC, e.month_of_year
            """, [code, month])
        else:
            cursor = conn.execute("""
                SELECT e.name, e.event_type, e.city, e.month_of_year, e.description,
                       e.annual_attendance, e.is_signature
                FROM state_events e
                JOIN states s ON e.state_id = s.id
                WHERE s.code = ?
                ORDER BY e.month_of_year
            """, [code])
        return [dict(r) for r in cursor.fetchall()]
    except sqlite3.Error:
        return []


@lru_cache(maxsize=32)
def get_all_states() -> list[dict[str, Any]]:
    """Return all top tourism states with summary info."""
    conn = _get_conn()
    if conn is None:
        return []
    try:
        cursor = conn.execute("""
            SELECT s.code, s.name, s.tourism_summary, s.tourism_economy_share,
                   COUNT(v.id) AS venue_count
            FROM states s
            LEFT JOIN venues v ON s.id = v.state_id
            WHERE s.is_top_tourism = 1
            GROUP BY s.id
            ORDER BY s.name
        """)
        return [dict(r) for r in cursor.fetchall()]
    except sqlite3.Error:
        return []


# ---------------------------------------------------------------------------
# Public API — nearby venues
# ---------------------------------------------------------------------------

@lru_cache(maxsize=128)
def get_venues_by_state_and_category(state_code: str, category: str) -> list[dict[str, Any]]:
    """Return venues in a state filtered by category.

    Accepts both 2-letter codes ("FL") and spelled-out names ("Florida").
    """
    code = _resolve_state_code(state_code)
    conn = _get_conn()
    if conn is None:
        return []
    try:
        cursor = conn.execute("""
            SELECT v.name, v.city, v.description, v.is_signature
            FROM venues v
            JOIN states s ON v.state_id = s.id
            WHERE s.code = ? AND v.category = ?
            ORDER BY v.is_signature DESC, v.name
        """, [code, category])
        return [dict(r) for r in cursor.fetchall()]
    except sqlite3.Error:
        return []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _default_hours(venue_type: str) -> str:
    """Return typical operating hours by venue category."""
    defaults = {
        "theme_park": "Typically 9:00 AM – 9:00 PM (varies by season)",
        "water_park": "Typically 10:00 AM – 5:00 PM (seasonal, March–October)",
        "museum": "Typically 10:00 AM – 5:30 PM (closed Mondays)",
        "zoo_aquarium": "Typically 9:00 AM – 5:00 PM",
        "national_park": "Typically sunrise to sunset; visitor centers 8:00 AM – 5:00 PM",
        "nature_park": "Typically sunrise to sunset",
        "historic_site": "Typically 9:00 AM – 5:00 PM",
        "resort_casino": "Open 24 hours; pools and restaurants vary",
        "entertainment_district": "Varies by venue; typically 10:00 AM – 2:00 AM",
        "entertainment_complex": "Typically 10:00 AM – midnight",
        "ski_resort": "Typically 8:30 AM – 4:00 PM (seasonal, November–April)",
        "music_venue": "Typically 7:00 PM – 11:00 PM (show nights vary)",
        "landmark": "Typically 24 hours for exterior; interior hours vary",
        "landmark_observatory": "Typically 8:00 AM – 2:00 AM (last elevator varies)",
        "urban_park": "Typically 6:00 AM – 1:00 AM",
        "garden": "Typically 9:00 AM – 5:00 PM",
        "wine_region": "Varies by winery; typically 10:00 AM – 5:00 PM",
        "beach": "Typically sunrise to sunset; lifeguards 9:00 AM – 5:00 PM",
        "scenic_drive": "Accessible 24 hours",
        "cultural_center": "Typically 10:00 AM – 6:00 PM",
        "nature_site": "Typically sunrise to sunset",
        "historic_district": "Outdoor accessible 24 hours; individual venues vary",
        "fairground": "Varies by event; typically 10:00 AM – 10:00 PM during fairs",
        "government_facility": "Typically 9:00 AM – 5:00 PM weekdays",
        "museum_working": "Typically 9:30 AM – 5:30 PM",
        "beach_nature": "Typically sunrise to sunset",
        "nature_region": "Accessible 24 hours; guided tours by appointment",
    }
    return defaults.get(venue_type, "Typically 9:00 AM – 5:00 PM")
