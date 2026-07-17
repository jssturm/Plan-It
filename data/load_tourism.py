#!/usr/bin/env python3
"""Load tourism schema and data into test.db."""
import sqlite3
import sys

DB_PATH = '/home/jstur/development/test.db'

def load_sql_file(conn, filepath):
    with open(filepath, 'r') as f:
        sql = f.read()
    # Split by semicolons and execute each statement
    conn.executescript(sql)
    print(f"  Executed: {filepath}")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Load schema first
    load_sql_file(conn, '/home/jstur/development/tourism_states.sql')
    # Load data
    load_sql_file(conn, '/home/jstur/development/tourism_data.sql')
    
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
    print("\nDone!")

if __name__ == '__main__':
    main()