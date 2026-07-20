"""Persistent plan store — survives server restarts and (on Vercel) warm-instance reuses.

Replaces the in-memory ``_plan_store: dict`` in ``app.main`` with a
SQLite-backed store that writes to disk.  On Vercel the filesystem is
ephemeral (plans are lost on cold start), but this is still a strict
improvement over the previous dict which was lost on *every* deployment
and between warm/cold boundaries within the same instance lifecycle.

For production use on Vercel, swap the backend to Vercel KV or Turso.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger("plan-it.plan_store")

# ---------------------------------------------------------------------------
# Database path — data dir for local dev, /tmp for Vercel serverless
# ---------------------------------------------------------------------------
def _store_path() -> Path:
    """Resolve the plan-store SQLite database path.

    On Vercel (detected via VERCEL env var) the filesystem is read-only
    except for /tmp, so we always use /tmp there.  Locally we prefer the
    project data/ directory for persistence across restarts.
    """
    # Explicit override for testing / custom deployments
    env_path = os.environ.get("PLAN_STORE_PATH")
    if env_path:
        return Path(env_path)

    # Vercel serverless — /tmp is the only writable directory
    if os.environ.get("VERCEL"):
        return Path("/tmp") / "plan-it-plans.db"

    # Local development — persist in the project data directory
    project_data = Path(__file__).resolve().parent.parent.parent / "data"
    if project_data.is_dir():
        try:
            # Verify the directory is writable before committing to it
            test_file = project_data / ".plan_store_write_test"
            test_file.touch()
            test_file.unlink()
            return project_data / "plans.db"
        except (OSError, PermissionError):
            pass

    # Fallback — /tmp always works
    return Path("/tmp") / "plan-it-plans.db"


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------
_conn: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        db_path = str(_store_path())
        _conn = sqlite3.connect(db_path, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA foreign_keys=ON")
        _conn.execute(
            """CREATE TABLE IF NOT EXISTS plans (
                plan_id     TEXT PRIMARY KEY,
                payload     TEXT NOT NULL,   -- JSON-serialized plan dict
                venue_type  TEXT,
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            )"""
        )
        _conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_plans_created ON plans(created_at)"
        )
        _conn.commit()
        logger.info("Plan store initialized at %s", db_path)
    return _conn


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def save_plan(plan: dict) -> str:
    """Store a plan and return its plan_id (generated if not present)."""
    conn = _get_conn()
    plan_id = plan.get("plan_id") or str(uuid.uuid4())
    plan["plan_id"] = plan_id
    venue_type = plan.get("venue_type", "")
    conn.execute(
        "INSERT OR REPLACE INTO plans (plan_id, payload, venue_type) VALUES (?, ?, ?)",
        [plan_id, json.dumps(plan, default=str), venue_type],
    )
    conn.commit()
    logger.info("Plan saved: %s (venue=%s)", plan_id[:8], venue_type)
    return plan_id


def get_plan(plan_id: str) -> dict | None:
    """Retrieve a plan by ID, or None if not found."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT payload FROM plans WHERE plan_id = ?", [plan_id]
    ).fetchone()
    if row is None:
        return None
    return json.loads(row["payload"])


def delete_plan(plan_id: str) -> bool:
    """Delete a plan. Returns True if a row was actually removed."""
    conn = _get_conn()
    cursor = conn.execute("DELETE FROM plans WHERE plan_id = ?", [plan_id])
    conn.commit()
    deleted = cursor.rowcount > 0
    if deleted:
        logger.info("Plan deleted: %s", plan_id[:8])
    return deleted


def update_plan(plan_id: str, plan: dict) -> str | None:
    """Replace the plan at *plan_id* with a new version, issuing a new ID.

    The original plan is deleted; the caller receives the new plan_id.
    Returns None when *plan_id* doesn't exist.
    """
    existing = get_plan(plan_id)
    if existing is None:
        return None
    delete_plan(plan_id)
    new_id = save_plan(plan)
    logger.info("Plan updated: %s → %s", plan_id[:8], new_id[:8])
    return new_id


def list_plans(limit: int = 50) -> list[dict]:
    """Return the most recent plans (up to *limit*)."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT payload FROM plans ORDER BY created_at DESC LIMIT ?", [limit]
    ).fetchall()
    return [json.loads(r["payload"]) for r in rows]


def plan_count() -> int:
    """Return the total number of stored plans."""
    conn = _get_conn()
    row = conn.execute("SELECT COUNT(*) AS cnt FROM plans").fetchone()
    return row["cnt"] if row else 0


def clear_all() -> int:
    """Delete all plans. Returns the number of rows removed."""
    conn = _get_conn()
    cursor = conn.execute("DELETE FROM plans")
    conn.commit()
    count = cursor.rowcount
    logger.info("All plans cleared (%d rows)", count)
    return count
