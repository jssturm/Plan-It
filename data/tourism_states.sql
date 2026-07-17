-- ================================================================
-- US TOP TOURISM STATES DATABASE
-- 9 States with their venues, parks, attractions & entertainment
-- ================================================================

-- ============================================================
-- SCHEMA: Core tables for multi-state tourism data
-- ============================================================

-- States table
CREATE TABLE IF NOT EXISTS states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    tourism_summary TEXT,
    tourism_economy_share TEXT,
    is_top_tourism BOOLEAN DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Venues (parks, museums, casinos, resorts, etc.)
CREATE TABLE IF NOT EXISTS venues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    city TEXT NOT NULL,
    region TEXT,
    parent_company TEXT,
    opening_year INTEGER,
    description TEXT,
    website TEXT,
    latitude REAL,
    longitude REAL,
    is_signature BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (state_id) REFERENCES states(id)
);

-- Attractions within venues
CREATE TABLE IF NOT EXISTS venue_attractions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    attraction_type TEXT NOT NULL,
    description TEXT,
    land_area TEXT,
    thrill_level TEXT CHECK(thrill_level IN ('none','mild','moderate','high','extreme')),
    height_requirement_inches INTEGER DEFAULT 0,
    opening_year INTEGER,
    is_signature BOOLEAN DEFAULT 0,
    is_defunct BOOLEAN DEFAULT 0,
    duration_minutes REAL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (venue_id) REFERENCES venues(id)
);

-- Land areas / themed sections within venues
CREATE TABLE IF NOT EXISTS venue_land_areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    theme TEXT,
    opening_year INTEGER,
    is_defunct BOOLEAN DEFAULT 0,
    FOREIGN KEY (venue_id) REFERENCES venues(id)
);

-- Events / festivals
CREATE TABLE IF NOT EXISTS state_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    event_type TEXT,
    city TEXT,
    month_of_year INTEGER CHECK(month_of_year BETWEEN 1 AND 12),
    description TEXT,
    annual_attendance INTEGER,
    is_signature BOOLEAN DEFAULT 0,
    FOREIGN KEY (state_id) REFERENCES states(id)
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_venues_state ON venues(state_id);
CREATE INDEX IF NOT EXISTS idx_venues_category ON venues(category);
CREATE INDEX IF NOT EXISTS idx_attractions_venue ON venue_attractions(venue_id);
CREATE INDEX IF NOT EXISTS idx_events_state ON state_events(state_id);