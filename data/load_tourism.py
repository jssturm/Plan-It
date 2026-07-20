#!/usr/bin/env python3
"""Load tourism schema and data into test.db.

Run from the Plan-It project root:
    python data/load_tourism.py

The database is created at data/test.db (relative to project root).
The app's db.py module searches for test.db in the same data/ directory.
"""
import sqlite3
import sys
from pathlib import Path

# Resolve paths relative to this script's location (Plan-It/data/)
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _SCRIPT_DIR.parent
_DB_PATH = _PROJECT_DIR / "data" / "test.db"


def load_sql_file(conn, filepath):
    with open(filepath, 'r') as f:
        sql = f.read()
    conn.executescript(sql)
    print(f"  Executed: {filepath}")


def main():
    # Ensure data directory exists
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")

    # Load schema first, then data
    schema_path = _SCRIPT_DIR / "tourism_states.sql"
    data_path = _SCRIPT_DIR / "tourism_data.sql"

    if not schema_path.is_file():
        print(f"ERROR: Schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(1)
    if not data_path.is_file():
        print(f"ERROR: Data file not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    load_sql_file(conn, str(schema_path))
    load_sql_file(conn, str(data_path))

    conn.commit()

    # Verify
    cursor = conn.execute("SELECT code, name FROM states ORDER BY code")
    print("\nStates loaded:")
    for row in cursor:
        print(f"  {row[0]} - {row[1]}")

    cursor = conn.execute("SELECT COUNT(*) FROM venues")
    print(f"\nTotal venues: {cursor.fetchone()[0]}")

    cursor = conn.execute("SELECT COUNT(*) FROM state_events")
    print(f"Total events: {cursor.fetchone()[0]}")

    cursor = conn.execute("SELECT COUNT(*) FROM venue_land_areas")
    print(f"Total land areas: {cursor.fetchone()[0]}")

    conn.close()
    print(f"\nDone! Database at: {_DB_PATH}")


if __name__ == '__main__':
    main()
