#!/usr/bin/env python3
"""Migrate Florida data from fl_* tables into the unified states/venues/venue_attractions/venue_land_areas schema."""
import sqlite3

DB_PATH = '/home/jstur/development/test.db'

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF")  # allow cross-inserts

    # 1. Insert Florida as a state
    conn.execute("""
        INSERT OR IGNORE INTO states (code, name, tourism_summary, tourism_economy_share, is_top_tourism)
        VALUES ('FL', 'Florida',
        'Orlando theme parks (Disney World, Universal), Miami beaches, Keys, Everglades, cruises; massive domestic + international leisure tourism',
        'Very High', 1)
    """)
    cursor = conn.execute("SELECT id FROM states WHERE code='FL'")
    fl_state_id = cursor.fetchone()[0]
    print(f"Florida state_id = {fl_state_id}")

    # 2. Migrate fl_parks -> venues
    # Build a mapping of old fl_parks id -> new venues id
    old_to_new = {}

    cursor = conn.execute("SELECT id, name, category, city, region, parent_company, opening_year, description, website FROM fl_parks")
    for row in cursor:
        old_id, name, category, city, region, parent_company, opening_year, description, website = row
        # Determine is_signature: major theme parks, national parks, and iconic venues
        is_sig = 1 if category in ('theme_park', 'national_park') or name in (
            'Kennedy Space Center Visitor Complex', 'Everglades National Park',
            'Dry Tortugas National Park', 'Biscayne National Park',
            'Key West Butterfly and Nature Conservatory', 'Ernest Hemingway Home and Museum',
            'Gatorland', 'Discovery Cove', 'Fun Spot America – Orlando',
            'Fun Spot America – Kissimmee', 'LEGOLAND Florida'
        ) else 0

        conn.execute("""
            INSERT INTO venues (state_id, name, category, city, region, parent_company, opening_year, description, website, is_signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fl_state_id, name, category, city, region, parent_company, opening_year, description, website, is_sig))

        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        old_to_new[old_id] = new_id

    print(f"Migrated {len(old_to_new)} venues")

    # 3. Migrate fl_land_areas -> venue_land_areas
    cursor = conn.execute("SELECT id, park_id, name, description, theme, opening_year, is_defunct FROM fl_land_areas")
    land_count = 0
    for row in cursor:
        land_id, park_id, name, description, theme, opening_year, is_defunct = row
        if park_id in old_to_new:
            new_venue_id = old_to_new[park_id]
            conn.execute("""
                INSERT INTO venue_land_areas (venue_id, name, description, theme, opening_year, is_defunct)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (new_venue_id, name, description, theme, opening_year, is_defunct))
            land_count += 1

    print(f"Migrated {land_count} land areas")

    # 4. Migrate fl_attractions -> venue_attractions
    cursor = conn.execute("""
        SELECT id, park_id, name, attraction_type, description, land_area,
               thrill_level, height_requirement_inches, opening_year, is_signature,
               is_defunct, duration_minutes
        FROM fl_attractions
    """)
    attr_count = 0
    for row in cursor:
        attr_id, park_id, name, attr_type, desc, land_area, thrill, height, open_year, is_sig, is_def, dur = row
        if park_id in old_to_new:
            new_venue_id = old_to_new[park_id]
            conn.execute("""
                INSERT INTO venue_attractions (venue_id, name, attraction_type, description, land_area,
                    thrill_level, height_requirement_inches, opening_year, is_signature, is_defunct, duration_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_venue_id, name, attr_type, desc, land_area, thrill, height, open_year, is_sig, is_def, dur))
            attr_count += 1

    print(f"Migrated {attr_count} attractions")

    # 5. Add Florida events
    fl_events = [
        ('Art Basel Miami Beach', 'art_fair', 'Miami Beach', 12, 'The premier art fair of the Americas with 250+ international galleries, satellite fairs, and VIP events across Miami.', 75000, 1),
        ('South Beach Wine & Food Festival', 'food_festival', 'Miami Beach', 2, 'Five-day star-studded culinary festival with 100+ events, Food Network personalities, and beachside tastings.', 65000, 1),
        ('Daytona 500', 'sporting_event', 'Daytona Beach', 2, 'The Great American Race, NASCAR''s biggest and most prestigious event kicking off the Cup Series season.', 101000, 1),
        ('Gasparilla Pirate Festival', 'cultural_festival', 'Tampa', 1, 'Tampa''s signature event with a pirate ship invasion, 3.5-hour parade of 100+ floats, and 300,000 beads thrown.', 300000, 1),
        ('Ultra Music Festival', 'music_festival', 'Miami', 3, 'Three-day electronic music festival at Bayfront Park drawing 165,000 attendees with world-class DJ lineups.', 165000, 1),
        ('Walt Disney World 50th+ Celebrations', 'theme_park_event', 'Lake Buena Vista', 10, 'Ongoing milestone celebrations across all four Disney parks with new nighttime spectaculars and attraction overlays.', 5000000, 1),
    ]

    for name, etype, city, month, desc, attendance, is_sig in fl_events:
        conn.execute("""
            INSERT INTO state_events (state_id, name, event_type, city, month_of_year, description, annual_attendance, is_signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (fl_state_id, name, etype, city, month, desc, attendance, is_sig))

    print(f"Added {len(fl_events)} Florida events")

    conn.commit()

    # Verify
    cursor = conn.execute("""
        SELECT s.code, s.name,
            COUNT(v.id) AS venues,
            COUNT(DISTINCT va.id) AS attractions,
            COUNT(DISTINCT vla.id) AS land_areas,
            COUNT(DISTINCT se.id) AS events
        FROM states s
        LEFT JOIN venues v ON s.id = v.state_id
        LEFT JOIN venue_attractions va ON v.id = va.venue_id
        LEFT JOIN venue_land_areas vla ON v.id = vla.venue_id
        LEFT JOIN state_events se ON s.id = se.state_id
        WHERE s.code = 'FL'
        GROUP BY s.id
    """)
    row = cursor.fetchone()
    print(f"\nFlorida migration summary: {row[2]} venues, {row[3]} attractions, {row[4]} land areas, {row[5]} events")

    conn.close()
    print("Done!")

if __name__ == '__main__':
    main()