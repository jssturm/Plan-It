"""Plan-It API -- FastAPI application with authentication, rate limiting, and observability."""

import copy
import logging
import os
import re
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.engine import calendar, plan_store
from app.engine.planner import build_travel_plan
from app.schemas.requests import TravelRequest

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
security = HTTPBearer(auto_error=False)


def require_auth(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> None:
    """Reject unauthenticated requests unless TRAVEL_API_KEY is unset (dev mode).

    In production, set TRAVEL_API_KEY in .env. Without it, all requests are
    allowed for local development convenience.
    """
    if not settings.API_KEY:
        # Dev mode: no auth required
        return

    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    if not _secure_compare(credentials.credentials, settings.API_KEY):
        raise HTTPException(status_code=403, detail="Invalid API key")


def _secure_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to avoid timing side-channels."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0


# ---------------------------------------------------------------------------
# Application lifespan (startup / shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Validate API key at startup and warn if misconfigured."""
    logger.info("Starting Plan-It v1")

    logger.info("Self-contained search engine — no external API keys required")
    logger.info("Using DuckDuckGo for web research and deterministic planner for itinerary construction")

    if settings.API_KEY:
        logger.info("API authentication is ENABLED (TRAVEL_API_KEY set)")
    else:
        logger.warning("API authentication is DISABLED -- set TRAVEL_API_KEY in .env to protect endpoints")

    logger.info("Rate limit: %s per remote address", settings.RATE_LIMIT)
    logger.info("Environment: %s", settings.ENVIRONMENT)

    yield  # App runs here

    logger.info("Shutting down Plan-It")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Plan-It",
    version="0.3.0",
    lifespan=lifespan,
    dependencies=[Depends(require_auth)],
)

# Rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Middleware: request logging
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every incoming request and its response status."""
    logger.info("%s %s from %s", request.method, request.url.path, get_remote_address(request))
    response = await call_next(request)
    logger.info("%s %s → %d", request.method, request.url.path, response.status_code)
    return response


# ---------------------------------------------------------------------------
# Patch request models
# ---------------------------------------------------------------------------
class ScheduleModification(BaseModel):
    """A single modification to apply to a plan's schedule."""

    action: str = Field(
        ...,
        description="One of: 'add', 'remove', 'reorder', 'update'",
        pattern=r"^(add|remove|reorder|update)$",
    )
    position: Optional[int] = Field(
        default=None,
        ge=0,
        description="0-based index for add/remove/reorder operations",
    )
    to_position: Optional[int] = Field(
        default=None,
        ge=0,
        description="Target 0-based index for reorder operations",
    )
    schedule_item: Optional[dict] = Field(
        default=None,
        description="Full schedule item object for add/update operations",
    )
    updates: Optional[dict] = Field(
        default=None,
        description="Partial schedule item fields to merge for update operations",
    )


class PlanUpdate(BaseModel):
    """Request body for PATCH /travel/{id}."""

    modifications: list[ScheduleModification] = Field(
        ...,
        min_length=1,
        description="Ordered list of schedule modifications to apply",
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health() -> dict:
    """Liveness check."""
    return {"status": "ok"}


@app.post("/travel")
@limiter.limit(settings.RATE_LIMIT)
def travel_plan(request: Request, payload: TravelRequest) -> dict:
    """Full Pydantic-validated itinerary, persisted for later modification.

    Accepts optional starting_location and restaurant_preferences to customize
    the generated itinerary. Plan is stored in a persistent SQLite-backed
    store and returned with a plan_id for future PATCH operations.
    """
    logger.info(
        "/travel requested: %s (start=%s, restaurant=%s)",
        payload.input[:80],
        payload.starting_location[:40] if payload.starting_location else "unspecified",
        payload.restaurant_preferences[:40] if payload.restaurant_preferences else "none",
    )

    try:
        result = build_travel_plan(
            user_input=payload.input,
            starting_location=payload.starting_location,
            restaurant_preferences=payload.restaurant_preferences,
            departure_time=payload.departure_time,
            default_reminder_min=payload.default_reminder_min,
        )
    except Exception as exc:
        logger.exception("Unhandled error in build_travel_plan")
        raise HTTPException(status_code=500, detail=f"Planner error: {exc}")

    if "error" not in result:
        try:
            plan_id = plan_store.save_plan(copy.deepcopy(result))
            result["plan_id"] = plan_id
            logger.info("Plan saved as %s", plan_id)
        except Exception as exc:
            # Persistence failure is non-fatal — return the plan without storing it
            logger.warning("Failed to persist plan (non-fatal): %s", exc)
            result["plan_id"] = "unsaved"
            result["_persist_error"] = str(exc)

    return result


@app.get("/travel/{plan_id}")
def get_plan(plan_id: str) -> dict:
    """Retrieve a previously generated plan by its ID."""
    plan = plan_store.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail=f"Plan not found: {plan_id}")
    return {"plan_id": plan_id, **{k: v for k, v in plan.items() if k != "plan_id"}}


@app.get("/travel/{plan_id}/calendar")
def download_calendar(plan_id: str, request: Request):
    """Download or subscribe to the itinerary as an iCalendar (.ics) file.

    - Browser access: downloads the .ics file for manual import.
    - Calendar app subscribe: use the URL directly in Google Calendar,
      Apple Calendar, or Outlook's 'Subscribe to Calendar' feature.
      The calendar app will poll this URL for updates.

    Each schedule item becomes a timed event with location links and
    reminder alarms.  Changes to the itinerary (via PATCH) are reflected
    on the next calendar app refresh.
    """
    plan = plan_store.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail=f"Plan not found: {plan_id}")

    ics_content = calendar.generate_icalendar(plan, plan_id)

    from fastapi.responses import Response

    # If the user-agent is a calendar app (or webcal:// protocol via redirect),
    # serve the content inline for subscription.  Browsers get a download.
    ua = request.headers.get("user-agent", "").lower()
    is_calendar_app = any(
        kw in ua for kw in ("calendar", "ical", "outlook", "caldav", "webcal")
    )

    headers: dict[str, str] = {}
    if is_calendar_app:
        headers["Content-Disposition"] = "inline"
    else:
        headers["Content-Disposition"] = (
            f'attachment; filename="plan-it-{plan_id[:8]}.ics"'
        )

    return Response(content=ics_content, media_type="text/calendar", headers=headers)


@app.patch("/travel/{plan_id}")
def modify_plan(plan_id: str, update: PlanUpdate) -> dict:
    """Modify a saved plan: add, remove, reorder, or update schedule items.

    **Operations:**

    - **add**: Insert a new schedule item at `position`. Provide `schedule_item`.
    - **remove**: Delete the schedule item at `position`.
    - **reorder**: Move item from `position` to `to_position`.
    - **update**: Merge `updates` dict into the schedule item at `position`.

    Modifications are applied in order. A new UUID is issued on each modification.
    """
    plan = plan_store.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail=f"Plan not found: {plan_id}")

    schedule = plan.get("schedule", [])
    if not isinstance(schedule, list):
        schedule = list(schedule)
        plan["schedule"] = schedule

    for idx, mod in enumerate(update.modifications):
        try:
            if mod.action == "add":
                if mod.schedule_item is None:
                    raise ValueError("'add' action requires schedule_item")
                insert_at = mod.position if mod.position is not None else len(schedule)
                schedule.insert(insert_at, mod.schedule_item)
                logger.info("[%s] add: inserted item at index %d", plan_id, insert_at)

            elif mod.action == "remove":
                if mod.position is None:
                    raise ValueError("'remove' action requires position")
                removed = schedule.pop(mod.position)
                logger.info("[%s] remove: deleted item at index %d (%s)", plan_id, mod.position, removed.get("action", "?"))

            elif mod.action == "reorder":
                if mod.position is None or mod.to_position is None:
                    raise ValueError("'reorder' action requires position and to_position")
                item = schedule.pop(mod.position)
                schedule.insert(mod.to_position, item)
                logger.info("[%s] reorder: moved %d → %d", plan_id, mod.position, mod.to_position)

            elif mod.action == "update":
                if mod.position is None or mod.updates is None:
                    raise ValueError("'update' action requires position and updates")
                if mod.position >= len(schedule):
                    raise IndexError(f"position {mod.position} out of range (schedule has {len(schedule)} items)")
                schedule[mod.position] = {**schedule[mod.position], **mod.updates}
                logger.info("[%s] update: merged updates into index %d", plan_id, mod.position)

        except (ValueError, IndexError) as exc:
            raise HTTPException(status_code=422, detail=f"Modification #{idx + 1} failed: {exc}")

    # Recalculate totals
    total_walk = 0
    total_wait = 0
    for item in schedule:
        if isinstance(item.get("walking_time_min"), (int, float)):
            total_walk += item["walking_time_min"]
        if isinstance(item.get("wait_time_min"), (int, float)):
            total_wait += item["wait_time_min"]
    plan["total_walking_min"] = total_walk
    plan["total_wait_min"] = total_wait

    # Issue new plan_id on modification so the original is preserved
    new_plan_id = plan_store.update_plan(plan_id, copy.deepcopy(plan))
    if new_plan_id is None:
        raise HTTPException(status_code=500, detail="Failed to persist plan update")
    logger.info("Modified plan saved as %s (was %s)", new_plan_id, plan_id)

    plan["plan_id"] = new_plan_id
    return {"plan_id": new_plan_id, **{k: v for k, v in plan.items() if k != "plan_id"}}


@app.post("/start-day")
@limiter.limit(settings.RATE_LIMIT)
def start_day(request: Request, payload: TravelRequest) -> dict:
    """
    Apple Shortcut bridge.

    Returns a flat dictionary compatible with Shortcuts'
    'Get Dictionary from Input' + 'Get Value from Dictionary' flow.

    Key fields at the top level (no nesting that Shortcuts can't parse):
      - next_map_url        → open in Maps
      - departure_time      → display
      - schedule            → array of strings (human-readable)
      - alerts              → array of strings
      - actions             → future-proof action queue
    """
    logger.info("/start-day requested: %s", payload.input[:80])
    try:
        result = build_travel_plan(
            user_input=payload.input,
            starting_location=payload.starting_location,
            restaurant_preferences=payload.restaurant_preferences,
        )
    except Exception as exc:
        logger.exception("Unhandled error in start-day build_travel_plan")
        raise HTTPException(status_code=500, detail=f"Planner error: {exc}")

    if "error" in result:
        return result

    route = result.get("route", [])
    schedule = result.get("schedule", [])
    next_map_url = route[0]["maps_url"] if route else ""
    departure_time = result.get("departure_time", "")

    schedule_lines = [f'{item["time"]} — {item["action"]}' for item in schedule]

    actions = [{"type": "open_maps", "url": next_map_url}] if next_map_url else []

    return {
        "next_map_url": next_map_url,
        "departure_time": departure_time,
        "schedule": schedule_lines,
        "alerts": result.get("alerts", []),
        "actions": actions,
    }


# ---------------------------------------------------------------------------
# Static file serving (mounted after API routes so they take precedence)
# ---------------------------------------------------------------------------
_static_dir = os.path.join(os.path.dirname(__file__), "..", "static")

# Asset URLs in served HTML get a fingerprint query so a browser refetches CSS/JS
# only when the file actually changes. Without it, cached styles survive updates.
_ASSET_REF = re.compile(r'(?P<attr>href|src)="(?P<path>/(?:css|js)/[^"?]+)"')


def _asset_fingerprint(url_path: str) -> str:
    try:
        return str(int(os.path.getmtime(os.path.join(_static_dir, url_path.lstrip("/")))))
    except OSError:
        return "0"


def _html_with_versioned_assets(path: str) -> HTMLResponse:
    with open(path, encoding="utf-8") as handle:
        html = handle.read()
    html = _ASSET_REF.sub(
        lambda m: f'{m.group("attr")}="{m.group("path")}?v={_asset_fingerprint(m.group("path"))}"',
        html,
    )
    # The document must revalidate, otherwise the new fingerprints stay invisible.
    return HTMLResponse(html, headers={"Cache-Control": "no-cache"})


if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

    @app.get("/app", dependencies=[], include_in_schema=False)
    async def serve_app():
        """Serve the main app UI."""
        app_path = os.path.join(_static_dir, "app.html")
        if os.path.isfile(app_path):
            return _html_with_versioned_assets(app_path)
        return {"status": "ok", "note": "Plan-It — app UI not found"}

    @app.get("/{full_path:path}", dependencies=[], include_in_schema=False)
    async def spa_fallback(full_path: str):
        """Serve static files or fall back to index.html for SPA routing."""
        # Serve actual static files at their expected paths (e.g. /css/app.css)
        file_path = os.path.join(_static_dir, full_path)
        if os.path.isfile(file_path) and not os.path.basename(file_path).startswith("."):
            return FileResponse(file_path)

        # SPA fallback — serve index.html for client-side routes
        index_path = os.path.join(_static_dir, "index.html")
        if os.path.isfile(index_path):
            return _html_with_versioned_assets(index_path)
        return {"status": "ok", "note": "Plan-It API — static UI not found"}
else:
    @app.get("/", include_in_schema=False)
    def root_no_ui():
        return {"status": "ok", "note": "Plan-It API running — no static UI mounted"}
