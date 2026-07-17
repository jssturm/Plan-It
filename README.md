# Plan-It

**Plan-It is a self-contained, AI-powered itinerary planning application.** Describe any trip in natural language — a theme park day, a museum visit, a weekend road trip, a national park hike, a festival outing, or a multi-day city tour — and the app produces a complete minute-by-minute itinerary optimized for that specific venue type.

Under the hood, it uses DuckDuckGo for real-time web research, a deterministic rules engine for itinerary construction, and optional DeepSeek AI for enhanced planning. Everything runs locally on your device — no cloud dependencies, no API keys required.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [SDK Install (Cross-Platform)](#sdk-install-cross-platform)
- [Quickstart (From Source)](#quickstart-from-source)
- [Configuration](#configuration)
- [CLI Reference](#cli-reference)
- [API Reference](#api-reference)
- [Frontend Overview](#frontend-overview)
- [Platform Support](#platform-support)
- [Development](#development)
- [License](#license)

---

## Features

### Core Itinerary Engine (No Cloud LLM Required)

| Feature | Detail |
|---------|--------|
| Natural-language intent parsing | Multi-stage parser extracts venue, location, time-of-day, and starting point from free text. Handles 40+ known venue aliases (e.g. "disney" → "Walt Disney World"), city-qualified venues ("Busch Gardens Tampa" vs "Busch Gardens Williamsburg"), and "from X" / "near Y" patterns |
| Venue-aware optimization | Auto-classifies destination as theme_park, museum, zoo, national_park, festival, city_tour, or general. Each type carries tailored defaults for opening hours, closing hours, maximum attractions, and departure times |
| Priority-tiered scheduling | First 3 attractions tagged high-priority, next 4 medium, remaining low. Wait times dynamically scale by time of day (5–15 min early morning, 15–45 min afternoon) |
| Multi-day trip detection | Automatic detection via text signals ("hotel", "overnight", "drive back", "check in") + drive-distance threshold (>4h round-trip). Generates Day 1 venue itinerary with hotel check-in + Day 2 return drive with midpoint lunch stop |
| Rest stop insertion | Long drives (>1h) automatically receive midpoint rest/meal stops every ~4 hours with meal-context labels (breakfast, lunch, dinner) based on cumulative drive time + departure hour |
| Venue open/close hour inference | Parses operating hours from web search results; falls back to type-specific defaults (theme parks: 7 AM–10 PM, museums: 9 AM–5 PM, national parks: 6 AM–8 PM, festivals: 10 AM–10 PM) |
| Curated attraction knowledge base | 40+ pre-vetted venues with specific ride/exhibit names: every major Disney/Universal park, SeaWorld, Busch Gardens Tampa & Williamsburg, Cedar Point, Six Flags Over Georgia, Kennedy Space Center, The Louvre, The Met, Smithsonian, San Diego & Bronx Zoos, 8 national parks (Yellowstone, Yosemite, Grand Canyon, Zion, Great Smoky Mountains, Rocky Mountain, Arches, Everglades), plus curated city attractions for New Orleans and San Antonio |
| Multi-tiered attraction matching | Curated lookup first by exact venue+location key, then fuzzy city-qualified match, exact venue name, substring match, and word-overlap fallback |
| Flight recommendation trigger | Trips with estimated one-way drive >12 hours automatically receive airline/flight recommendations with route, estimated price, and booking URLs |
| Departure time normalization | Accepts `7:00 AM`, `07:00`, `7am`, `0700`, `7:00AM`, bare hour integers — normalizes all to canonical `HH:MM AM/PM` format |

### Web Research Engine (Zero API Keys)

| Feature | Detail |
|---------|--------|
| DuckDuckGo search client | Self-contained — zero API keys, zero authentication. Rate-limited at 1.2s between queries to respect fair use |
| Venue research (6 queries per plan) | Researches visitor guides, hours, tickets, top attractions, crowd tips, and parking info from web results |
| Restaurant intelligence | Searches for real restaurants near venue; filters out 15+ garbage patterns (aggregator pages, "Top 10 Best" listicles, hotel restaurants, generic search pages). Returns cuisine, price range, location, and notes. Supports dietary/cuisine preference filtering |
| Hotel search with fallback database | Searches for 3+ star hotels near destination; validates results against 70+ known hotel chains. Falls back to curated hotel database for 6 cities (Tampa, Orlando, Miami, Atlanta, New York, Paris) when search returns garbage |
| Dual-layer geocoding | Tier 1: US Census Bureau geocoder (free, no rate limit, handles structured US addresses). Tier 2: Nominatim/OpenStreetMap (global fallback, 1 req/s). Parse street/city/state/zip from comma-separated addresses |
| OSRM real road-network routing | Converts addresses to lat/lon via geocoding, calls the public OSRM routing API for actual drive duration on real roads. Returns human-readable driving time + distance in miles |
| US state name/code normalization | Supports all 50 states + DC, Puerto Rico, Guam, USVI. Accepts both "FL" and "Florida", resolves to 2-letter codes for geocoding |
| Cuisine inference | Classifies 18 cuisine types from text: Italian, Mexican, Japanese, Chinese, American, French, Thai, Indian, Mediterranean, Seafood, Steakhouse, BBQ, Korean, Vietnamese, and more |
| Price range detection | Infers $-$$$$ from text descriptors ("cheap"/"budget" → $, "moderate"/"mid-range" → $$, "upscale"/"fine dining" → $$$) |
| Midpoint city inference | Known midpoint cities for 10 common route pairs (Jacksonville→Tampa ≈ Gainesville, Orlando→Miami ≈ West Palm Beach, Atlanta→Orlando ≈ Valdosta, etc.) |
| Transit/driving route construction | Generates ordered Google Maps directions URLs for every route leg, including return legs for multi-day trips |
| Rental car recommendations | Pre-loaded with Enterprise, Hertz, and Avis options with car type, daily rate, and pickup location per destination |
| Ride share estimates | Uber and Lyft estimates with cost, time, and route per origin-destination pair |

### Traffic & Alert Intelligence

| Feature | Detail |
|---------|--------|
| Known corridor traffic warnings | Pattern-matched alerts for I-4 Orlando corridor, I-95 Miami/Jacksonville, Atlanta metro I-75/I-85, and Tampa Bay I-275 bridge traffic |
| Contextual rush-hour estimates | Each alert includes time-of-day guidance: "I-4 can add 30+ minutes during peak hours", "I-95 congestion common 7-9 AM and 4-7 PM" |
| Alert de-duplication | Case-insensitive dedup of all alerts before delivery, capped at 5 |
| Strategy notes synthesis | Crowd-tip extraction from web results + parking guidance appended as actionable strategy notes |

### API & Backend Infrastructure

| Feature | Detail |
|---------|--------|
| FastAPI REST API | OpenAPI-compliant with automatic interactive docs at `/docs`. Version 0.3.0 |
| Pydantic validation (10+ models) | Full schema validation for TravelPlan, Stop, ScheduleItem, RentalCar, RideShare, ParkingOption, Flight, Hotel, TravelRequest, PlanUpdate, ScheduleModification |
| PATCH-based schedule editing | Four mutation operations: `add` (insert at position), `remove` (delete at index), `reorder` (move position→to_position), `update` (merge partial fields). New UUID issued per mutation. Operations applied in order |
| In-memory plan store | UUID-keyed plan storage for server lifetime; plans retrievable via `GET /travel/{plan_id}` |
| Per-IP rate limiting | Configurable via `slowapi`; defaults to 10 requests/minute per remote address |
| Bearer token API auth | Optional — enabled when `TRAVEL_API_KEY` is set; constant-time comparison to prevent timing attacks. Disabled in dev mode (no key set) |
| Request logging middleware | Every request logged with method, path, remote address, and response status |
| Apple Shortcut bridge | `/start-day` endpoint returns flat dict format for iOS Shortcuts compatibility |
| Cloudflare Tunnel wrapper | `tunnel.sh` auto-reconnect script for exposing the server publicly |
| DeepSeek AI integration (optional) | Set `DEEPSEEK_API_KEY` to enable enhanced planning via `deepseek-chat`, `deepseek-reasoner`, or `deepseek-coder` models |
| Multi-agent framework | `app/agents/` — extensible agent system for specialized planning tasks |
| SQLite tourism knowledge base | `app/engine/db.py` — multi-state venue/attraction/POI lookups from a SQLite database |
| Health endpoint | `GET /health` returns `{"status": "ok"}` for liveness probing |

### Frontend (Vanilla JS SPA — Zero Build Step)

| Feature | Detail |
|---------|--------|
| Trip generation | Natural-language input + optional starting location + departure time (HH:MM + AM/PM toggle) + restaurant preferences → inline rendered itinerary |
| Inline result preview | On the New Trip page, results render immediately with stats grid, color-coded timeline, route legs, flights, hotels, parking, ride shares, alerts, strategy notes |
| Full itinerary view | Dedicated Plan Detail page with same rich layout + edit/delete controls |
| Plan management | All generated plans saved to `sessionStorage`; sidebar displays last 10 with venue type labels and short IDs; "My Plans" page shows all with metadata cards (departure, stops, legs, walking/wait totals) |
| Schedule editing | Full modal form: edit time (with AM/PM toggle), action, priority, walking time, wait time, restaurant, reminder interval, walking map URL, meal timing note, backup plan. Add new stops, remove existing stops — all via PATCH API |
| Inline reminder system | Per-item configurable reminder (5–60 min, in 5-min increments) via inline dropdown. On trigger, automatically opens the walking map URL in a new tab with a toast notification. Tracks fired reminders in `sessionStorage` to prevent duplicates |
| Confirm modal | Destructive actions (plan deletion) require explicit confirmation |
| API health monitor | Live indicator dot (green online / red offline) polling every 30 seconds |
| Toast notifications | Success/error/info toast with auto-dismiss for all user actions |
| Responsive design | Collapsible sidebar on mobile; responsive grid layouts; stats grid and card grids adapt to viewport |
| Keyboard shortcuts | `Ctrl+Enter` to generate an itinerary |
| Session persistence | `sessionStorage`-backed plan store survives page reloads |
| City-state validation | Warns on ambiguous city names (e.g. "Jacksonville" without state) to improve geocoding accuracy |
---

## Architecture

```
plan-it/
├── app/
│   ├── __init__.py
│   ├── cli.py                 # CLI entry point (plan-it command)
│   ├── config.py              # Environment-based settings
│   ├── env_detect.py          # Cross-platform environment detection
│   ├── main.py                # FastAPI app, endpoints, middleware
│   ├── agents/                # Multi-agent planning system
│   │   └── __init__.py
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── db.py              # SQLite tourism knowledge base (venue/attraction lookups)
│   │   ├── osrm.py            # Real-world drive time lookup + city extraction
│   │   ├── search.py          # DuckDuckGo search client (zero API keys)
│   │   └── planner.py         # Deterministic itinerary builder
│   ├── llm/                   # DeepSeek AI integration
│   │   └── __init__.py
│   └── schemas/
│       ├── __init__.py
│       ├── itinerary.py       # TravelPlan, Stop, ScheduleItem models
│       └── requests.py        # TravelRequest input model
├── static/
│   ├── index.html             # SPA shell
│   ├── css/
│   │   └── app.css            # Design system
│   └── js/
│       └── app.js             # Vanilla JS SPA
├── data/                      # SQL migration scripts for tourism database
│   ├── florida_attractions.sql
│   ├── load_tourism.py
│   ├── migrate_florida.py
│   ├── tourism_data.sql
│   └── tourism_states.sql
├── install.sh                 # Unix cross-platform installer
├── install.ps1                # Windows PowerShell installer
├── tunnel.sh                  # Cloudflare Tunnel auto-reconnect wrapper
├── pyproject.toml             # Package manifest
├── requirements.txt           # Python dependencies
├── test_deepseek.py           # DeepSeek API integration test
├── test_travel.py             # Integration test suite
├── SHORTCUT_SETUP.md          # iPhone Shortcuts setup guide
└── README.md
```

**Data flow:**

```
User Input (browser) → POST /travel → planner.py → intent parser → venue detection
                                                            ↓
                                            SQLite tourism DB (venue/attraction lookups)
                                            DuckDuckGo search (venue, restaurants, transit, hotels)
                                            DeepSeek AI (optional — enhanced planning when DEEPSEEK_API_KEY set)
                                                            ↓
                                            OSRM drive times → route + schedule construction
                                                            ↓
                                            Pydantic TravelPlan validation
                                                            ↓
Browser ← JSON response ← in-memory plan store (UUID-keyed) ← validated plan
```

---

## SDK Install (Cross-Platform)

Plan-It ships as a pip-installable package (`plan-it`) with a `plan-it` CLI command. No API keys required — works out of the box with DuckDuckGo. Add `DEEPSEEK_API_KEY` for enhanced AI planning.

### Prerequisites

- **Python 3.12+** (required on all platforms)
- Internet access (for DuckDuckGo web research)
- Optional: `DEEPSEEK_API_KEY` for AI-enhanced planning via DeepSeek

### Quick Install (recommended)

```bash
pip install plan-it
plan-it serve
```

On Windows use `python -m pip install plan-it`. Open http://localhost:8000 when the server starts.

### Installer script (with auto-start service)

The full installer creates a virtual environment, configures shell integration, and optionally sets up auto-start on boot. Download and run the platform installer:

**macOS / Linux / WSL:**
```bash
curl -fsSL -o install.sh https://raw.githubusercontent.com/jssturm/Plan-It/main/install.sh
bash install.sh
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/jssturm/Plan-It/main/install.ps1 -OutFile install.ps1
.\install.ps1
```

> **Note:** If the repo is private, use `gh api` or a Personal Access Token to fetch the installer. The `pip install` path above works without repo access.

| Flag | `install.sh` | `install.ps1` | Description |
|------|-------------|---------------|-------------|
| Quick mode | `--quick` | `-Quick` | Non-interactive with defaults |
| Force reinstall | `--force` | `-Force` | Reinstall even if already configured |
| Dry run | `--dry-run` | `-DryRun` | Validate environment without installing |

**Service control (macOS):**
```bash
launchctl start com.plan-it.app
launchctl stop com.plan-it.app
```

**Service control (Linux/WSL):**
```bash
systemctl --user start plan-it
systemctl --user stop plan-it
journalctl --user -u plan-it -f
```

### Android (Termux)

```bash
pkg install python git
python -m pip install plan-it
plan-it serve --host 127.0.0.1 --port 8000
# Open http://127.0.0.1:8000 in Chrome
```

### iOS (iSH)

```bash
apk add python3
python3 -m pip install plan-it
plan-it serve --host 127.0.0.1 --port 8000
# Open http://127.0.0.1:8000 in Safari
```

### Dry run (validate without installing)

```bash
bash install.sh --dry-run
```

Checks Python version, pip, curl, disk space, and OS compatibility without making changes.


### Cloudflare Tunnel (optional — expose server publicly)

Use `tunnel.sh` to expose your local server via Cloudflare Tunnel with automatic reconnection:

```bash
./tunnel.sh [port]  # default: 8000
```

Requires `cloudflared` installed at `~/.local/bin/cloudflared`.

---

## Quickstart (From Source)

### Prerequisites

- Python 3.12+
- Optional: SQLite tourism database (copy `test.db` to project root or set `JEFFOS_DB_PATH`)
- Optional: `DEEPSEEK_API_KEY` for AI-enhanced planning

### 1. Clone and set up

```bash
git clone https://github.com/jssturm/Plan-It.git
cd Plan-It
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the server

```bash
plan-it serve
```

### 3. Open the UI

Navigate to **http://localhost:8000** in your browser.

No configuration needed — the app works immediately using DuckDuckGo for web research and the built-in SQLite tourism database for venue lookups.

### 4. Optional: Enable DeepSeek AI

```bash
export DEEPSEEK_API_KEY=sk-your-key-here
plan-it serve
```

With `DEEPSEEK_API_KEY` set, the planner uses DeepSeek for enhanced itinerary generation alongside the deterministic rules engine.

---

## Configuration

Optional environment variables loaded from `.env`:

When installed with the SDK, config is stored per-platform:

| Platform | Config Location |
|----------|----------------|
| macOS | `~/.config/plan-it/.env` |
| Windows | `%LOCALAPPDATA%\plan-it\config\.env` |
| Linux | `~/.config/plan-it/.env` or `$XDG_CONFIG_HOME/plan-it/.env` |
| Android | `~/.config/plan-it/.env` |
| iOS | `~/.config/plan-it/.env` |

Override with the `TRAVEL_ENV_PATH` environment variable.

| Variable | Default | Description |
|----------|---------|-------------|
| `TRAVEL_API_KEY` | *(empty — no auth)* | If set, endpoints require `Authorization: Bearer <key>` |
| `DEEPSEEK_API_KEY` | *(empty — disabled)* | If set, enables DeepSeek AI for enhanced itinerary planning |
| `DEEPSEEK_MODEL` | `deepseek-chat` | DeepSeek model to use: `deepseek-chat`, `deepseek-reasoner`, or `deepseek-coder` |
| `JEFFOS_DB_PATH` | *(auto-detected)* | Path to SQLite tourism database (defaults to project root `test.db`) |
| `RATE_LIMIT` | `10/minute` | Per-IP rate limit |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |
| `SEARCH_MAX_RESULTS` | `12` | Max DuckDuckGo results per query |
| `SEARCH_RATE_LIMIT_S` | `1.2` | Seconds between DuckDuckGo queries |
| `MAX_INPUT_LENGTH` | `2000` | Maximum user input length |
| `ENVIRONMENT` | `production` | Logging context |
| `TRAVEL_HOST` | `0.0.0.0` | Server bind address |
| `TRAVEL_PORT` | `8000` | Server port |

---

## CLI Reference

```bash
plan-it             # Show help and available commands
plan-it init        # Bootstrap environment and create .env file
plan-it serve       # Start the API server
plan-it check       # Print environment diagnostics
plan-it doctor      # Full diagnostics (env, deps, network)
```

**`plan-it serve` options:**

| Flag | Description |
|------|-------------|
| `--host HOST` | Bind address (default: `0.0.0.0`) |
| `--port PORT` | Port (default: `8000`) |
| `--reload` | Enable auto-reload on file changes |
| `--no-reload` | Disable auto-reload |
| `--log-level LEVEL` | One of: `critical`, `error`, `warning`, `info`, `debug` |

---

## API Reference

### `GET /health`

Liveness check. No authentication required.

**Response:** `{ "status": "ok" }`

### `POST /travel`

Generate a full travel itinerary.

**Request:**
```json
{
  "input": "Plan my trip to Kennedy Space Center tomorrow with lunch stop",
  "starting_location": "Hyatt Regency Orlando, 9801 International Dr",
  "restaurant_preferences": "vegetarian, prefer Italian, $$-$$$",
  "departure_time": "07:30 AM"
}
```

**Response:** Full `TravelPlan` JSON object with `route`, `schedule`, `alerts`, `strategy_notes`, `hotels`, `flights`, `rental_cars`, `ride_shares`, `parking_options`, and totals.

### `GET /travel/{plan_id}` — Retrieve a plan by ID.
### `PATCH /travel/{plan_id}` — Modify schedule items (add, remove, reorder, update).
### `POST /start-day` — Apple Shortcut bridge (flat dict response). See `SHORTCUT_SETUP.md` for iPhone integration guide.

---

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| macOS (Apple Silicon/Intel) | ✅ Full | `launchd` service, Brew Python |
| Windows 10/11 (x86_64) | ✅ Full | Scheduled task, winget Python |
| Linux (x86_64/ARM64) | ✅ Full | `systemd` user service |
| WSL 2 | ✅ Full | Access from Windows browser at `localhost:8000` |
| Android (Termux) | ✅ Local | Server on-device; Chrome access |
| iOS (iSH) | ✅ Local | Server on-device; Safari access |

---

## Development

### Running tests

```bash
# Integration tests (FastAPI TestClient)
python -m pytest test_travel.py -v

# DeepSeek API integration test
DEEPSEEK_API_KEY=sk-... python test_deepseek.py
```

### Building the SDK package
```bash
python3 -m pip install build
python3 -m build
# Outputs: dist/plan-it-0.3.0.tar.gz and .whl
```

### Publishing to PyPI
```bash
python3 -m pip install twine
python3 -m twine upload dist/*
```

### Local test install
```bash
pip install -e .
plan-it serve
```

### Environment Detection (`app/env_detect.py`)

Cross-platform module that identifies the OS, Python version, available tools, and correct config/data paths at runtime. Powers `plan-it check` and `plan-it doctor` across macOS, Windows, Linux, WSL, Android (Termux), and iOS (iSH).

### SQLite Tourism Database (`app/engine/db.py`)

Queries a multi-state SQLite tourism knowledge base for venue lookups, attraction details, and points of interest. Database path is resolved from `JEFFOS_DB_PATH` env var or auto-detected from the project root. Data migration scripts are in the `data/` directory.

### OSRM Routing (`app/engine/osrm.py`)

Provides real-world drive time estimates between common city pairs using a comprehensive lookup table — no external API calls or rate limits. Includes smart city-name extraction from full street addresses.

### DeepSeek AI Integration (`app/llm/`)

When `DEEPSEEK_API_KEY` is set, the planner leverages DeepSeek models for enhanced itinerary generation. Supports all three DeepSeek models: `deepseek-chat` (V3), `deepseek-reasoner` (R1 with chain-of-thought), and `deepseek-coder` (structured output).

### Multi-Agent System (`app/agents/`)

Extensible agent framework for specialized planning tasks. Agents can be composed to handle different aspects of trip planning (venue research, restaurant recommendations, route optimization).

---

## License

[MIT](LICENSE)