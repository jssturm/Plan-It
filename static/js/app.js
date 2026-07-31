/* ==========================================================================
   Plan-It — Client Application
   ==========================================================================
   A vanilla JS SPA that talks to the Plan-It API.
   Covers: itinerary generation, plan storage, schedule editing, and
   dashboard-style plan review.
   ========================================================================== */

(function () {
  "use strict";

  /* ------------------------------------------------------------------------
     Configuration
     ------------------------------------------------------------------------ */
  // i18n — gracefully degrade if i18n.js isn't loaded
  var t = window.t || function (k, s) { return k; };
  var setLang = window.setLanguage || function () {};
  var getCurrentLang = window.getCurrentLanguage || function () { return "en"; };
  const API_BASE = window.location.origin;
  const PLANS_KEY = "plan-it_plans";
  const THEME_KEY = "Plan-It:theme";

  /* ------------------------------------------------------------------------
     Theme Management (dark / light)
     ------------------------------------------------------------------------ */
  function getTheme() {
    try {
      var stored = localStorage.getItem(THEME_KEY);
      if (stored === "dark" || stored === "light") return stored;
    } catch (e) {}
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    var html = document.documentElement;
    var isDark = theme === "dark";
    if (isDark) {
      html.classList.add("dark");
    } else {
      html.classList.remove("dark");
    }
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) {}
    updateThemeToggleUI(isDark);
  }

  function toggleTheme() {
    var isDark = document.documentElement.classList.contains("dark");
    applyTheme(isDark ? "light" : "dark");
  }

  function updateThemeToggleUI(isDark) {
    var icon = document.getElementById("theme-toggle-icon");
    var label = document.getElementById("theme-toggle-label");
    var topbarIcon = document.getElementById("theme-toggle-icon-topbar");
    if (icon) icon.textContent = isDark ? "☀️" : "🌙";
    if (label) label.textContent = isDark ? "Light" : "Dark";
    if (topbarIcon) topbarIcon.textContent = isDark ? "☀️" : "🌙";
  }

  function initTheme() {
    applyTheme(getTheme());
    var btn = document.getElementById("theme-toggle");
    var topbarBtn = document.getElementById("theme-toggle-topbar");
    if (btn) btn.addEventListener("click", toggleTheme);
    if (topbarBtn) topbarBtn.addEventListener("click", toggleTheme);
    // Listen for system preference changes
    try {
      window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (e) {
        // Only auto-switch if user hasn't set a preference
        try { if (localStorage.getItem(THEME_KEY)) return; } catch (_) {}
        applyTheme(e.matches ? "dark" : "light");
      });
    } catch (e) {}
  }

  /* ------------------------------------------------------------------------
     DOM Refs (lazy-initialized after DOMContentLoaded)
     ------------------------------------------------------------------------ */
  let $ = (sel) => document.querySelector(sel);
  let $$ = (sel) => document.querySelectorAll(sel);

  // Sidebar
  let $sidebar, $sidebarOverlay, $mobileMenuBtn, $healthDot, $healthLabel, $planCountBadge,
      $sidebarSavedPlans, $clearBtn;

  // Topbar
  let $topbarTitle;

  // Pages
  let $pageNewTrip, $pageMyPlans, $pagePlanDetail;
  let $resultNewTrip, $plansList, $plansEmpty, $planDetailContent,
      $planDetailTitle, $planDetailSubtitle;

  // Form
  let $tripInput, $tripStart, $tripDepartureHh, $tripDepartureMm, $tripDepartureAmpm, $tripRestaurants, $tripReminderDefault, $btnGenerate;

  // Modal
  let $modalContainer;

  // Toast
  let $toastContainer;

  /* ------------------------------------------------------------------------
     State
     ------------------------------------------------------------------------ */
  let currentPage = "new-trip";
  let currentPlanId = null;
  let planStore = {}; // { plan_id: plan_object }
  let firedReminders = {}; // { "planId-scheduleIndex": true }

  /* ------------------------------------------------------------------------
     Initialization
     ------------------------------------------------------------------------ */
  function init() {
    cacheDom();
    initTheme();
    loadPlanStore();
    loadFiredReminders();
    bindEvents();
    checkHealth();
    setInterval(checkHealth, 30000); // poll health every 30s
    setInterval(checkReminders, 30000); // check for due reminders every 30s
    checkReminders(); // run immediately on init
    navigateTo("new-trip");
  }

  function loadFiredReminders() {
    try {
      var raw = sessionStorage.getItem("travel_fired_reminders");
      firedReminders = raw ? JSON.parse(raw) : {};
    } catch (e) {
      firedReminders = {};
    }
  }

  function saveFiredReminders() {
    sessionStorage.setItem("travel_fired_reminders", JSON.stringify(firedReminders));
  }

  function checkReminders() {
    var now = new Date();
    var currentMinutes = now.getHours() * 60 + now.getMinutes();

    Object.keys(planStore).forEach(function (planId) {
      var plan = planStore[planId];
      if (!Array.isArray(plan.schedule)) return;

      plan.schedule.forEach(function (item, idx) {
        if (!item.reminder_min || !item.time) return;
        var key = planId + "-" + idx;
        if (firedReminders[key]) return; // already fired

        var eventTime = parseTimeString(item.time);
        if (eventTime === null) return;

        // The reminder should fire when current time >= (event_time - reminder_min)
        var reminderTime = eventTime - item.reminder_min;
        if (currentMinutes >= reminderTime && currentMinutes < eventTime) {
          // Fire the reminder — open the map
          firedReminders[key] = true;
          saveFiredReminders();

          var mapUrl = item.walking_map_url;
          if (!mapUrl && item.map_destination) {
            mapUrl = buildWalkingMapsUrl(null, item.map_destination);
          }
          if (!mapUrl) {
            // Fall back to the route maps_url if available
            var routeIdx = findRouteIndexForSchedule(plan, idx);
            if (routeIdx >= 0 && Array.isArray(plan.route) && plan.route[routeIdx]) {
              mapUrl = plan.route[routeIdx].maps_url;
            }
          }

          if (mapUrl) {
            window.open(mapUrl, "_blank", "noopener,noreferrer");
            showToast(t("toast.reminderFiredMap", { time: item.time }), "info");
          } else {
            showToast(t("toast.reminderFired", { time: item.time, action: item.action }), "info");
          }
        }
      });
    });
  }

  function parseTimeString(timeStr) {
    var match = timeStr.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
    if (!match) return null;
    var hours = parseInt(match[1], 10);
    var mins = parseInt(match[2], 10);
    var period = match[3].toUpperCase();
    if (period === "PM" && hours < 12) hours += 12;
    if (period === "AM" && hours === 12) hours = 0;
    return hours * 60 + mins;
  }

  function findRouteIndexForSchedule(plan, scheduleIdx) {
    if (!Array.isArray(plan.route) || plan.route.length === 0) return scheduleIdx;
    var scheduleLen = Array.isArray(plan.schedule) ? plan.schedule.length : 0;
    var routeLen = plan.route.length;
    if (scheduleLen <= routeLen) return scheduleIdx;
    return Math.min(scheduleIdx, routeLen - 1);
  }

  function cacheDom() {
    $sidebar = $("#sidebar");
    $sidebarOverlay = $("#sidebar-overlay");
    $mobileMenuBtn = $("#mobile-menu-btn");
    $healthDot = $("#health-dot");
    $healthLabel = $("#health-label");
    $planCountBadge = $("#plan-count-badge");
    $sidebarSavedPlans = $("#sidebar-saved-plans");
    $clearBtn = $("#btn-clear-store");
    $topbarTitle = $("#topbar-title");

    $pageNewTrip = $("#page-new-trip");
    $pageMyPlans = $("#page-my-plans");
    $pagePlanDetail = $("#page-plan-detail");

    $resultNewTrip = $("#result-new-trip");
    $plansList = $("#plans-list");
    $plansEmpty = $("#plans-empty");
    $planDetailContent = $("#plan-detail-content");
    $planDetailTitle = $("#plan-detail-title");
    $planDetailSubtitle = $("#plan-detail-subtitle");

  $tripInput = $("#trip-input");
  $tripStart = $("#trip-start");
  $tripDepartureHh = $("#trip-departure-hh");
  $tripDepartureMm = $("#trip-departure-mm");
  $tripDepartureAmpm = $("#trip-departure-ampm");
  $tripRestaurants = $("#trip-restaurants");
  $tripReminderDefault = $("#trip-reminder-default");
  $btnGenerate = $("#btn-generate");

    $modalContainer = $("#modal-container");
    $toastContainer = $("#toast-container");
  }

  /* ------------------------------------------------------------------------
     Plan Store (sessionStorage)
     ------------------------------------------------------------------------ */
  function loadPlanStore() {
    try {
      const raw = sessionStorage.getItem(PLANS_KEY);
      planStore = raw ? JSON.parse(raw) : {};
    } catch (e) {
      planStore = {};
    }
    updatePlanBadge();
    renderSidebarSavedPlans();
  }

  function savePlanStore() {
    sessionStorage.setItem(PLANS_KEY, JSON.stringify(planStore));
    updatePlanBadge();
    renderSidebarSavedPlans();
  }

  function addPlanToStore(plan) {
    planStore[plan.plan_id] = Object.assign({}, plan);
    // Strip plan_id from inside the stored object since we key on it
    savePlanStore();
  }

  function removePlanFromStore(planId) {
    delete planStore[planId];
    savePlanStore();
  }

  function updatePlanInStore(planId, plan) {
    planStore[planId] = Object.assign({}, plan);
    savePlanStore();
  }

  function clearPlanStore() {
    planStore = {};
    savePlanStore();
  }

  /* ------------------------------------------------------------------------
     Sidebar
     ------------------------------------------------------------------------ */
  function updatePlanBadge() {
    const count = Object.keys(planStore).length;
    if (count > 0) {
      $planCountBadge.style.display = "";
      $planCountBadge.textContent = count;
    } else {
      $planCountBadge.style.display = "none";
    }
  }

  function renderSidebarSavedPlans() {
    const ids = Object.keys(planStore);
    if (ids.length === 0) {
      $sidebarSavedPlans.innerHTML =
          '<div class="text-xs text-muted" style="padding: var(--space-2) var(--space-3);">' + t("nav.noSavedPlans") + '</div>';
      return;
    }
    $sidebarSavedPlans.innerHTML = ids
      .slice(-10) // last 10
      .reverse()
      .map((id) => {
        const plan = planStore[id];
        const label = plan.venue_type
          ? capitalize(plan.venue_type.replace(/_/g, " "))
          : "Trip";
        return `
          <button class="nav-item" data-plan-id="${escapeHtml(id)}" data-action="open-plan">
            <span class="nav-item-icon">&#128205;</span>
            <span class="truncate">${escapeHtml(label)}</span>
            <span class="text-xs text-muted font-mono" style="margin-left:auto;">${escapeHtml(id.slice(0, 8))}</span>
          </button>`;
      })
      .join("");
  }

  /* ------------------------------------------------------------------------
     Routing
     ------------------------------------------------------------------------ */
  function navigateTo(page, data) {
    currentPage = page;

    // Close mobile sidebar when navigating
    closeMobileSidebar();

    // Update nav items
    $$(".nav-item[data-page]").forEach((el) => {
      el.classList.toggle("active", el.dataset.page === page);
    });

    // Toggle pages
    $pageNewTrip.classList.toggle("hidden", page !== "new-trip");
    $pageMyPlans.classList.toggle("hidden", page !== "my-plans");
    $pagePlanDetail.classList.toggle("hidden", page !== "plan-detail");

    // Update topbar title
    const titles = {
      "new-trip": t("topbar.newTrip"),
      "my-plans": t("topbar.myPlans"),
      "plan-detail": t("topbar.itinerary"),
    };
    $topbarTitle.textContent = titles[page] || "Plan-It";

    // Page-specific setup
    if (page === "my-plans") {
      renderPlansList();
    } else if (page === "plan-detail" && data && data.planId) {
      currentPlanId = data.planId;
      renderPlanDetail(data.planId);
    } else if (page === "new-trip") {
      // Always reset to a clean slate when navigating to New Trip
      $tripInput.value = "";
      $tripStart.value = "";
      if ($tripDepartureHh) $tripDepartureHh.value = "";
      if ($tripDepartureMm) $tripDepartureMm.value = "";
      resetAmpmToggle();
      $tripRestaurants.value = "";
      $resultNewTrip.classList.add("hidden");
      if (data && data.scrollToResult) {
        $resultNewTrip.scrollIntoView({ behavior: "smooth" });
      }
      setTimeout(function () { $tripInput.focus(); }, 0);
    }
  }

  /* ------------------------------------------------------------------------
     API Client
     ------------------------------------------------------------------------ */
  async function apiGet(path) {
    const res = await fetch(API_BASE + path, {
      headers: { Accept: "application/json" },
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `HTTP ${res.status}`);
    }
    return res.json();
  }

  async function apiPost(path, payload) {
    const res = await fetch(API_BASE + path, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `HTTP ${res.status}`);
    }
    return res.json();
  }

  async function apiPatch(path, payload) {
    const res = await fetch(API_BASE + path, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `HTTP ${res.status}`);
    }
    return res.json();
  }

  /* ------------------------------------------------------------------------
     Actions
     ------------------------------------------------------------------------ */
  async function generateTrip() {
    const input = $tripInput.value.trim();
    if (!input) {
      showToast(t("error.describeTrip"), "error");
      return;
    }

    const start = $tripStart.value.trim();
    // Address validation removed — Nominatim handles free-form geocoding
    // for any reasonable input (city names, addresses, landmarks, etc.)

    // Check for city names without a state — duplicate cities exist
    // (e.g. Jacksonville FL/TX/NC, Portland OR/ME, Springfield IL/MO/MA)
    const cityErr = validateCityState(input);
    if (cityErr) {
      showToast(cityErr, "error");
      return;
    }

    $btnGenerate.disabled = true;
    $btnGenerate.innerHTML = '<span class="spinner"></span> ' + t("newTrip.generating");
    $resultNewTrip.classList.add("hidden");

    try {
      const payload = { input };
      const hh = $tripDepartureHh ? $tripDepartureHh.value.trim() : "";
      const mm = $tripDepartureMm ? $tripDepartureMm.value.trim() : "";
      const departurePeriod = getSelectedPeriod();
      var departure = "";
      if (hh || mm) {
        // Validate time before constructing the departure string
        var timeErr = validateTimeInput(hh, mm);
        if (timeErr) {
          showToast(timeErr, "error");
          $btnGenerate.disabled = false;
          $btnGenerate.innerHTML = "&#128640; Generate Itinerary";
          return;
        }
        departure = (hh || "00") + ":" + (mm || "00");
        if (departurePeriod) departure = departure + " " + departurePeriod;
      }
      const restaurants = $tripRestaurants.value.trim();
      if (start) payload.starting_location = start;
      if (departure) payload.departure_time = departure;
      if (restaurants) payload.restaurant_preferences = restaurants;
      if ($tripReminderDefault && $tripReminderDefault.checked) {
        payload.default_reminder_min = 15;
      }

      const plan = await apiPost("/travel", payload);

      if (plan.error) {
        showToast(plan.error, "error");
        return;
      }

      // Store locally
      addPlanToStore(plan);
      currentPlanId = plan.plan_id;

      // Render the result inline
      renderPlanResultInline(plan);
      $resultNewTrip.classList.remove("hidden");
      $resultNewTrip.scrollIntoView({ behavior: "smooth" });
      showToast(t("toast.itineraryGenerated"), "success");
    } catch (err) {
      showToast(err.message || t("error.failedGenerate"), "error");
    } finally {
      $btnGenerate.disabled = false;
      $btnGenerate.innerHTML = t("newTrip.generate");
    }
  }

  async function checkHealth() {
    try {
      const data = await apiGet("/health");
      if (data.status === "ok") {
        $healthDot.className = "health-dot online";
        $healthLabel.textContent = t("health.online");
      } else {
        throw new Error("unexpected status");
      }
    } catch {
      $healthDot.className = "health-dot offline";
      $healthLabel.textContent = t("health.unreachable");
    }
  }

  /* ------------------------------------------------------------------------
     Render: Inline Result (New Trip page)
     ------------------------------------------------------------------------ */
  function renderPlanResultInline(plan) {
    $resultNewTrip.innerHTML = `
    <div class="section">
      <div class="section-header">
        <span class="section-title">${t("section.itinerary")}</span>
          <div class="flex items-center gap-3">
            <span class="plan-card-venue">${escapeHtml(capitalize((plan.venue_type || "general").replace(/_/g, " ")))}</span>
            <span class="text-xs text-muted font-mono">${escapeHtml(plan.plan_id.slice(0, 8))}</span>
          </div>
        </div>

        ${renderCrowdBadge(plan)}
        ${renderStatsGrid(plan)}
        ${renderSchedule(plan)}
        ${renderRoute(plan)}
        ${renderFlights(plan)}
        ${renderParking(plan)}
        ${renderRentalCars(plan)}
        ${renderRideShares(plan)}
        ${renderHotels(plan)}
        ${renderAlerts(plan)}
        ${renderStrategy(plan)}
        ${renderTotalsBar(plan)}

        <div class="flex gap-3" style="margin-top: var(--space-6);">
          <button class="btn btn-primary" id="btn-view-full" data-plan-id="${escapeHtml(plan.plan_id)}">
            ${t("schedule.viewFull")}
          </button>
          <a class="btn btn-secondary" href="/travel/${escapeHtml(plan.plan_id)}/calendar" download="${'plan-it-' + escapeHtml(plan.plan_id.slice(0, 8)) + '.ics'}">
            &#128197; ${t("schedule.downloadCalendar")}
          </a>
          <button class="btn btn-secondary" id="btn-new-plan">
            ${t("schedule.planAnother")}
          </button>
        </div>
      </div>
    `;

    // Bind inline buttons
    const viewFullBtn = $resultNewTrip.querySelector("#btn-view-full");
    const newPlanBtn = $resultNewTrip.querySelector("#btn-new-plan");
    if (viewFullBtn) {
      viewFullBtn.addEventListener("click", () => {
        navigateTo("plan-detail", { planId: plan.plan_id });
      });
    }
    if (newPlanBtn) {
      newPlanBtn.addEventListener("click", () => {
      $tripInput.value = "";
      $tripStart.value = "";
      if ($tripDepartureHh) $tripDepartureHh.value = "";
      if ($tripDepartureMm) $tripDepartureMm.value = "";
      resetAmpmToggle();
      $tripRestaurants.value = "";
      $resultNewTrip.classList.add("hidden");
      $tripInput.focus();
      });
    }
  }

  /* ------------------------------------------------------------------------
     Render: Plan Detail page
     ------------------------------------------------------------------------ */
  function renderPlanDetail(planId) {
    const plan = planStore[planId];
    if (!plan) {
      $planDetailContent.innerHTML =
        '<div class="empty-state"><div class="empty-state-icon">&#128269;</div><div class="empty-state-title">' + t("planDetail.notFound") + '</div><div class="empty-state-text">' + t("planDetail.notFoundText") + '</div></div>';
      $planDetailTitle.textContent = t("planDetail.notFound");
      $planDetailSubtitle.textContent = "";
      return;
    }

    $planDetailTitle.textContent =
      capitalize((plan.venue_type || "general").replace(/_/g, " ")) + " Itinerary";
    $planDetailSubtitle.innerHTML = `
      <span class="plan-card-venue">${escapeHtml(capitalize((plan.venue_type || "general").replace(/_/g, " ")))}</span>
      &nbsp;&middot;&nbsp;
      <span class="font-mono text-xs text-muted">${escapeHtml(planId.slice(0, 8))}</span>
      &nbsp;&middot;&nbsp;
      <span class="text-xs text-muted">Departure: ${escapeHtml(plan.departure_time || "—")}</span>
    `;

    $planDetailContent.innerHTML = `
      ${renderCrowdBadge(plan)}
      ${renderStatsGrid(plan)}
      ${renderSchedule(plan, true)}
      ${renderRoute(plan)}
      ${renderFlights(plan)}
      ${renderParking(plan)}
      ${renderRentalCars(plan)}
      ${renderRideShares(plan)}
      ${renderHotels(plan)}
      ${renderAlerts(plan)}
      ${renderStrategy(plan)}
      ${renderTotalsBar(plan)}

      <div class="flex gap-3" style="margin-top: var(--space-6);">
        <a class="btn btn-primary btn-sm" href="/travel/${escapeHtml(planId)}/calendar" download="${'plan-it-' + escapeHtml(planId.slice(0, 8)) + '.ics'}">
          &#128197; ${t("schedule.downloadCalendar")}
        </a>
        <button class="btn btn-secondary btn-sm" id="btn-print-plan">
          &#128424; ${t("schedule.print")}
        </button>
        <button class="btn btn-secondary btn-sm" id="btn-share-plan" data-plan-id="${escapeHtml(planId)}">
          &#128279; ${t("schedule.share")}
        </button>
        <button class="btn btn-danger btn-sm" id="btn-delete-plan" data-plan-id="${escapeHtml(planId)}">
          ${t("planDetail.delete")}
        </button>
      </div>
    `;

    // Bind print
    const printBtn = $planDetailContent.querySelector("#btn-print-plan");
    if (printBtn) {
      printBtn.addEventListener("click", () => { window.print(); });
    }

    // Bind share
    const shareBtn = $planDetailContent.querySelector("#btn-share-plan");
    if (shareBtn) {
      shareBtn.addEventListener("click", () => {
        var shareUrl = window.location.origin + "/travel/" + shareBtn.dataset.planId;
        if (navigator.clipboard) {
          navigator.clipboard.writeText(shareUrl).then(function () {
            showToast(t("toast.linkCopied"), "success");
          }).catch(function () {
            showToast(shareUrl, "info");
          });
        } else {
          // Fallback for older browsers
          var ta = document.createElement("textarea");
          ta.value = shareUrl;
          ta.style.position = "fixed"; ta.style.opacity = "0";
          document.body.appendChild(ta); ta.select();
          document.execCommand("copy");
          document.body.removeChild(ta);
          showToast(t("toast.linkCopied"), "success");
        }
      });
    }

    // Bind delete
    const delBtn = $planDetailContent.querySelector("#btn-delete-plan");
    if (delBtn) {
      delBtn.addEventListener("click", () => {
        showConfirmModal(
          t("planDetail.deleteTitle"),
          t("planDetail.deleteConfirm"),
          () => {
            removePlanFromStore(planId);
            showToast(t("toast.planDeleted"), "info");
            navigateTo("my-plans");
          }
        );
      });
    }
  }

  /* ------------------------------------------------------------------------
     Render: My Plans list
     ------------------------------------------------------------------------ */
  function renderPlansList() {
    const ids = Object.keys(planStore).reverse();
    if (ids.length === 0) {
      $plansList.innerHTML = "";
      $plansEmpty.classList.remove("hidden");
      return;
    }
    $plansEmpty.classList.add("hidden");
    $plansList.innerHTML = ids
      .map((id) => {
        const plan = planStore[id];
        const scheduleCount = Array.isArray(plan.schedule) ? plan.schedule.length : 0;
        const routeCount = Array.isArray(plan.route) ? plan.route.length : 0;
        return `
          <div class="plan-card" data-plan-id="${escapeHtml(id)}" data-action="open-plan">
            <div class="plan-card-header">
              <span class="plan-card-venue">${escapeHtml(capitalize((plan.venue_type || "general").replace(/_/g, " ")))}</span>
              <span class="plan-card-id">${escapeHtml(id.slice(0, 8))}</span>
            </div>
            <div class="plan-card-meta">
              <span>&#128337; ${escapeHtml(plan.departure_time || "—")}</span>
              <span>&#128345; ${scheduleCount} stops</span>
              <span>&#128739; ${routeCount} legs</span>
              ${plan.total_walking_min != null ? `<span>&#128099; ${plan.total_walking_min}min walk</span>` : ""}
              ${plan.total_wait_min != null ? `<span>&#9203; ${plan.total_wait_min}min wait</span>` : ""}
            </div>
          </div>`;
      })
      .join("");
  }

  /* ------------------------------------------------------------------------
     Render Helpers — Shared Components
     ------------------------------------------------------------------------ */
  function renderCrowdBadge(plan) {
    if (plan.crowd_level == null) return "";
    var level = plan.crowd_level;
    var label, colorClass;
    if (level >= 8) { label = t("crowd.packed"); colorClass = "crowd-high"; }
    else if (level >= 6) { label = t("crowd.busy"); colorClass = "crowd-med"; }
    else if (level >= 4) { label = t("crowd.moderate"); colorClass = "crowd-low"; }
    else { label = t("crowd.light"); colorClass = "crowd-low"; }
    return '<div class="crowd-banner ' + colorClass + '">'
      + '<span class="crowd-banner-icon">&#128205;</span>'
      + '<span>' + t("crowd.predictedCrowd", { level: level }) + ' — ' + label + '</span>'
      + '</div>';
  }

  function renderStatsGrid(plan) {
    const scheduleLen = Array.isArray(plan.schedule) ? plan.schedule.length : 0;
    const highPriority = Array.isArray(plan.schedule)
      ? plan.schedule.filter((s) => s.priority === "high").length
      : 0;
    return `
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-label">${t("stats.departure")}</span>
          <span class="stat-value">${escapeHtml(plan.departure_time || "—")}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">${t("stats.stops")}</span>
          <span class="stat-value">${scheduleLen}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">${t("stats.highPriority")}</span>
          <span class="stat-value">${highPriority}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">${t("stats.venue")}</span>
          <span class="stat-value" style="font-size:var(--text-lg);">${escapeHtml(capitalize((plan.venue_type || "general").replace(/_/g, " ")))}</span>
        </div>
      </div>
    `;
  }

  function renderSchedule(plan, editable) {
    if (!Array.isArray(plan.schedule) || plan.schedule.length === 0) {
      return '<div class="text-sm text-muted">' + t("schedule.noItems") + '</div>';
    }

    const venueName = plan.venue_name || "";
    const items = plan.schedule
      .map((item, idx) => {
        const prioClass = item.priority || "medium";
        const metaBadges = [];
        if (item.walking_time_min != null) {
          metaBadges.push(
            '<span class="badge badge-walk">' + t("badge.walk", { min: item.walking_time_min }) + '</span>'
          );
        }
        if (item.wait_time_min != null) {
          metaBadges.push(
            '<span class="badge badge-wait">' + t("badge.wait", { min: item.wait_time_min }) + '</span>'
          );
        }
        if (item.reminder_min) {
          metaBadges.push(
            '<span class="badge badge-reminder" title="' + t("modal.field.reminder") + '">' + t("badge.reminder", { min: item.reminder_min }) + '</span>'
          );
        }
        if (item.restaurant) {
          metaBadges.push(
            `<span class="badge badge-restaurant">&#127860; ${escapeHtml(item.restaurant)}</span>`
          );
        }
        if (item.backup_plan) {
          metaBadges.push(
            `<span class="badge badge-backup">&#128737; ${escapeHtml(item.backup_plan)}</span>`
          );
        }
        metaBadges.push(
          '<span class="badge badge-priority ' + prioClass + '">' + t("badge.priority." + item.priority) + '</span>'
        );

        const editControls = editable
          ? `
          <div class="schedule-item-actions">
            <button class="btn btn-sm btn-ghost edit-schedule-btn" data-index="${idx}" title="${t("modal.editTitle")}">${t("schedule.edit")}</button>
            <button class="btn btn-sm btn-ghost remove-schedule-btn" data-index="${idx}" title="${t("schedule.removeTitle")}" style="color:var(--color-danger)">${t("schedule.remove")}</button>
          </div>`
          : "";

        const currentReminder = item.reminder_min || "";
        const reminderOptions = [
          "", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60"
        ];
        var reminderSelect = '<select class="reminder-inline" data-plan-id="' + escapeHtml(plan.plan_id) + '" data-schedule-index="' + idx + '" title="' + t("modal.field.reminder") + '">'
              + reminderOptions.map(function (v) {
                var label = v === "" ? t("schedule.reminderNone") : t("schedule.reminderMin", { min: v });
                var sel = String(currentReminder) === String(v) ? " selected" : "";
                return '<option value="' + v + '"' + sel + '>' + label + '</option>';
              }).join("")
            + '</select>';

        var mapDest = resolveMapDestination(item, venueName);
        var mapActions = "";
        if (mapDest || item.walking_map_url) {
          mapActions = '<div class="schedule-map-actions">';
          if (mapDest) {
            mapActions +=
              '<button type="button" class="btn btn-sm btn-primary map-from-here-btn" ' +
              'data-destination="' + escapeHtml(mapDest) + '" ' +
              'title="' + t("schedule.mapFromHereHint") + '">' +
              t("schedule.mapFromHere") +
              "</button>";
          }
          if (item.walking_map_url) {
            mapActions +=
              '<a href="' + escapeHtml(item.walking_map_url) + '" target="_blank" rel="noopener" ' +
              'class="btn btn-sm btn-secondary walk-from-prev-btn">' +
              t("schedule.walkFromPrev") +
              "</a>";
          }
          mapActions += "</div>";
        }

        return `
          <div class="timeline-item" data-schedule-index="${idx}">
            <div class="timeline-dot ${prioClass}"></div>
            <button type="button" class="timeline-item-header" aria-expanded="false" data-schedule-index="${idx}">
              <div class="timeline-item-header-main">
                <span class="timeline-time">${escapeHtml(item.time || "—")}</span>
                <span class="timeline-action">${escapeHtml(item.action)}</span>
              </div>
              <span class="timeline-expand-icon" aria-hidden="true">&#9660;</span>
            </button>
            <div class="timeline-item-body" hidden>
              ${editControls}
              ${item.meal_timing_note ? `<div class="text-xs text-muted mb-2">&#128161; ${escapeHtml(item.meal_timing_note)}</div>` : ""}
              ${mapActions}
              <div class="timeline-meta">${reminderSelect}${metaBadges.join("")}</div>
            </div>
          </div>`;
      })
      .join("");

    const addBtn = editable
      ? `
  <div style="margin-top: var(--space-4);">
    <button class="btn btn-sm btn-secondary" id="btn-add-schedule-item">
      ${t("schedule.addStop")}
    </button>
  </div>`
      : "";

    return `
      <div class="section">
        <div class="section-header">
          <span class="section-title">${t("section.schedule")}</span>
          <span class="text-xs text-muted">${t("schedule.tapToExpand")}</span>
        </div>
        <div class="card">
          <div class="timeline" id="schedule-timeline">${items}</div>
          ${addBtn}
        </div>
      </div>
    `;
  }

  /** Prefer explicit map_destination; else Maps URL dest; else "Visit X" / venue. */
  function resolveMapDestination(item, venueName) {
    if (item && item.map_destination) return String(item.map_destination).trim();
    if (item && item.walking_map_url) {
      try {
        var u = new URL(item.walking_map_url);
        var dest = u.searchParams.get("destination");
        if (dest) return decodeURIComponent(dest.replace(/\+/g, " "));
      } catch (e) { /* ignore */ }
    }
    var action = (item && item.action) ? String(item.action) : "";
    var visit = action.match(/^Visit\s+(.+?)(?:\s+—|$)/i);
    if (visit) {
      var place = visit[1].split(" — ")[0].trim();
      if (venueName && place.toLowerCase().indexOf(venueName.toLowerCase()) === -1) {
        return place + ", " + venueName;
      }
      return place;
    }
    if (venueName && /arrive at/i.test(action)) return venueName;
    return "";
  }

  function buildWalkingMapsUrl(origin, destination) {
    var url = "https://www.google.com/maps/dir/?api=1&destination=" +
      encodeURIComponent(destination) + "&travelmode=walking";
    if (origin) {
      url += "&origin=" + encodeURIComponent(origin);
    }
    return url;
  }

  function openWalkingMapFromHere(destination) {
    if (!destination) {
      showToast(t("schedule.mapNoDestination"), "error");
      return;
    }
    function openWithOrigin(origin) {
      window.open(buildWalkingMapsUrl(origin, destination), "_blank", "noopener,noreferrer");
    }
    if (!navigator.geolocation) {
      openWithOrigin(null);
      showToast(t("schedule.mapOpenedNoGeo"), "info");
      return;
    }
    showToast(t("schedule.locating"), "info");
    navigator.geolocation.getCurrentPosition(
      function (pos) {
        openWithOrigin(pos.coords.latitude + "," + pos.coords.longitude);
        showToast(t("schedule.mapOpened"), "success");
      },
      function () {
        openWithOrigin(null);
        showToast(t("schedule.mapOpenedNoGeo"), "info");
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  }

  /** Expand/collapse stops and map-from-here — shared by plan detail + inline result. */
  function handleScheduleUiClick(e) {
    var mapBtn = e.target.closest(".map-from-here-btn");
    if (mapBtn) {
      e.preventDefault();
      e.stopPropagation();
      openWalkingMapFromHere(mapBtn.getAttribute("data-destination") || "");
      return;
    }

    var header = e.target.closest(".timeline-item-header");
    if (!header) return;
    // Ignore clicks that bubbled from controls inside the expanded body
    if (e.target.closest(".timeline-item-body")) return;

    var item = header.closest(".timeline-item");
    if (!item) return;
    var body = item.querySelector(".timeline-item-body");
    if (!body) return;

    var willOpen = body.hasAttribute("hidden");
    // Accordion: close other open stops in the same timeline
    var timeline = item.closest(".timeline");
    if (timeline && willOpen) {
      timeline.querySelectorAll(".timeline-item.is-expanded").forEach(function (el) {
        if (el === item) return;
        el.classList.remove("is-expanded");
        var h = el.querySelector(".timeline-item-header");
        var b = el.querySelector(".timeline-item-body");
        if (h) h.setAttribute("aria-expanded", "false");
        if (b) b.setAttribute("hidden", "");
      });
    }

    if (willOpen) {
      body.removeAttribute("hidden");
      item.classList.add("is-expanded");
      header.setAttribute("aria-expanded", "true");
    } else {
      body.setAttribute("hidden", "");
      item.classList.remove("is-expanded");
      header.setAttribute("aria-expanded", "false");
    }
  }

  function renderRoute(plan) {
    if (!Array.isArray(plan.route) || plan.route.length === 0) {
      return "";
    }
    const legs = plan.route
      .map(
        (leg, idx) => `
      <div class="route-leg">
        <div class="route-leg-index">${idx + 1}</div>
        <div class="route-leg-body">
          <div class="route-leg-step">${escapeHtml(leg.step)}</div>
          <a href="${escapeHtml(leg.maps_url)}" target="_blank" rel="noopener" class="route-leg-url">
            ${t("route.openMaps")}
          </a>
        </div>
      </div>`
      )
      .join("");
    return `
      <div class="section">
        <div class="section-header">
          <span class="section-title">${t("section.route")}</span>
        </div>
        ${legs}
      </div>
    `;
  }

  function renderAlerts(plan) {
    if (!Array.isArray(plan.alerts) || plan.alerts.length === 0) {
      return "";
    }
    return `
      <div class="section">
        <div class="section-header">
          <span class="section-title">${t("section.alerts")}</span>
        </div>
        <div class="alert-list">
          ${plan.alerts.map((a) => `<div class="alert-item">&#9888; ${escapeHtml(a)}</div>`).join("")}
        </div>
      </div>
    `;
  }

  function renderStrategy(plan) {
    if (!Array.isArray(plan.strategy_notes) || plan.strategy_notes.length === 0) {
      return "";
    }
    return `
      <div class="section">
        <div class="section-header">
          <span class="section-title">${t("section.strategy")}</span>
        </div>
        <div class="strategy-list">
          ${plan.strategy_notes.map((s) => `<div class="strategy-item">&#128161; ${escapeHtml(s)}</div>`).join("")}
        </div>
      </div>
    `;
  }

  function renderParking(plan) {
    if (!Array.isArray(plan.parking_options) || plan.parking_options.length === 0) {
      return "";
    }
    var cards = plan.parking_options.map(function (p) {
      return '<div class="parking-card">'
        + '<div class="parking-name">' + escapeHtml(p.name) + '</div>'
        + '<div class="parking-type">' + escapeHtml(p.type) + '</div>'
        + '<div class="parking-meta">'
        + '<span>&#128176; ' + escapeHtml(p.daily_rate) + '</span>'
        + '<span>' + escapeHtml(p.location) + '</span>'
        + '</div>'
        + (p.shuttle ? '<div class="parking-shuttle text-xs text-muted">&#128652; ' + escapeHtml(p.shuttle) + '</div>' : '')
        + (p.booking_url ? '<a href="' + escapeHtml(p.booking_url) + '" target="_blank" rel="noopener" class="btn btn-sm btn-secondary">' + t("btn.reserveParking") + '</a>' : '')
        + '</div>';
    }).join("");
    return '<div class="section">'
      + '<div class="section-header"><span class="section-title">' + t("section.parking") + '</span></div>'
      + '<div class="parking-grid">' + cards + '</div>'
      + '</div>';
  }

  function renderFlights(plan) {
    if (!Array.isArray(plan.flights) || plan.flights.length === 0) {
      return "";
    }
    var cards = plan.flights.map(function (f) {
      return '<div class="flight-card">'
        + '<div class="flight-airline">' + escapeHtml(f.airline) + '</div>'
        + '<div class="flight-route">&#9992; ' + escapeHtml(f.route) + '</div>'
        + '<div class="flight-meta">'
        + '<span>&#128176; ' + escapeHtml(f.estimated_price) + '</span>'
        + '<span>&#128339; ' + escapeHtml(f.flight_time) + '</span>'
        + '</div>'
        + '<a href="' + escapeHtml(f.booking_url) + '" target="_blank" rel="noopener" class="btn btn-sm btn-primary">' + t("btn.searchFlights") + '</a>'
        + '</div>';
    }).join("");
    return '<div class="section">'
      + '<div class="section-header"><span class="section-title">' + t("section.flights") + '</span></div>'
      + '<div class="flights-grid">' + cards + '</div>'
      + '</div>';
  }

  function renderRentalCars(plan) {
    if (!Array.isArray(plan.rental_cars) || plan.rental_cars.length === 0) {
      return "";
    }
    var cards = plan.rental_cars.map(function (rc) {
      return '<div class="rental-car-card">'
        + '<div class="rental-car-name">' + escapeHtml(rc.company) + '</div>'
        + '<div class="rental-car-type">' + escapeHtml(rc.car_type) + '</div>'
        + '<div class="rental-car-meta">'
        + '<span>' + escapeHtml(rc.estimated_daily_rate) + '</span>'
        + '<span>' + escapeHtml(rc.pickup_location) + '</span>'
        + '</div>'
        + '<a href="' + escapeHtml(rc.booking_url) + '" target="_blank" rel="noopener" class="btn btn-sm btn-secondary">' + t("btn.compareCars") + '</a>'
        + '</div>';
    }).join("");
    return '<div class="section">'
      + '<div class="section-header"><span class="section-title">' + t("section.rentalCars") + '</span></div>'
      + '<div class="rental-cars-grid">' + cards + '</div>'
      + '</div>';
  }

  function renderRideShares(plan) {
    if (!Array.isArray(plan.ride_shares) || plan.ride_shares.length === 0) {
      return "";
    }
    var shares = plan.ride_shares.map(function (rs) {
      return '<div class="ride-share-card">'
        + '<div class="ride-share-service">'
        + '<span class="badge badge-accent">' + escapeHtml(rs.service) + '</span>'
        + '</div>'
        + '<div class="ride-share-route">' + escapeHtml(rs.route) + '</div>'
        + '<div class="ride-share-meta">'
        + '<span>&#128176; ' + escapeHtml(rs.estimated_cost) + '</span>'
        + '<span>&#128339; ' + escapeHtml(rs.estimated_time) + '</span>'
        + '</div>'
        + (rs.app_url ? '<a href="' + escapeHtml(rs.app_url) + '" target="_blank" rel="noopener" class="btn btn-sm btn-secondary">' + t("btn.openApp") + '</a>' : '')
        + '</div>';
    }).join("");
    return '<div class="section">'
      + '<div class="section-header"><span class="section-title">' + t("section.rideShares") + '</span></div>'
      + '<div class="ride-shares-grid">' + shares + '</div>'
      + '</div>';
  }

  function renderHotels(plan) {
    if (!Array.isArray(plan.hotels) || plan.hotels.length === 0) {
      return "";
    }
    var stars = function (n) {
      var s = '';
      for (var i = 0; i < n; i++) s += '&#11088;';
      return s;
    };
    var hotelCards = plan.hotels.map(function (h) {
      return '<div class="hotel-card">'
        + '<div class="hotel-name">' + escapeHtml(h.name) + '</div>'
        + '<div class="hotel-stars">' + stars(h.star_rating) + ' <span class="text-muted text-xs">' + h.star_rating + '-star</span></div>'
        + '<div class="hotel-meta">'
        + '<span>' + escapeHtml(h.price_range) + '</span>'
        + '<span>' + escapeHtml(h.location) + '</span>'
        + '</div>'
        + (h.highlights ? '<div class="hotel-highlights text-sm text-secondary">' + escapeHtml(h.highlights) + '</div>' : '')
        + '<a href="' + escapeHtml(h.booking_url) + '" target="_blank" rel="noopener" class="btn btn-sm btn-secondary mt-2">' + t("btn.bookNow") + '</a>'
        + '</div>';
    }).join("");
    return '<div class="section">'
      + '<div class="section-header"><span class="section-title">' + t("section.hotels") + '</span></div>'
      + '<div class="hotels-grid">' + hotelCards + '</div>'
      + '</div>';
  }

  function renderTotalsBar(plan) {
    if (plan.total_walking_min == null && plan.total_wait_min == null) return "";
    return `
      <div class="totals-bar">
        ${plan.total_walking_min != null ? '<div class="totals-item"><span class="totals-label">' + t("totals.walking") + '</span><span class="totals-value">' + plan.total_walking_min + ' ' + t("totals.min") + '</span></div>' : ""}
        ${plan.total_wait_min != null ? '<div class="totals-item"><span class="totals-label">' + t("totals.waiting") + '</span><span class="totals-value">' + plan.total_wait_min + ' ' + t("totals.min") + '</span></div>' : ""}
      </div>
    `;
  }

  /* ------------------------------------------------------------------------
     Schedule Editing (PATCH-based)
     ------------------------------------------------------------------------ */
  async function patchScheduleItem(planId, action, index, extra) {
    const modifications = [{ action, position: index }];
    if (extra) Object.assign(modifications[0], extra);

    const updated = await apiPatch(`/travel/${planId}`, { modifications });
    // Replace old plan with the new one (new plan_id issued)
    removePlanFromStore(planId);
    addPlanToStore(updated);
    return updated;
  }

  function openEditModal(planId, item, index) {
    const plan = planStore[planId];
    if (!plan || !item) return;

    const fields = [
      { key: "time", label: "Time (HH:MM AM/PM)" },
      { key: "action", label: "Action" },
      { key: "priority", label: "Priority (high/medium/low)", type: "select", options: ["high", "medium", "low"] },
      { key: "walking_time_min", label: "Walking Time (min)", type: "number" },
      { key: "wait_time_min", label: "Wait Time (min)", type: "number" },
      { key: "restaurant", label: "Restaurant" },
      { key: "reminder_min", label: "Reminder Before (min)", type: "select", options: ["", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60"] },
      { key: "walking_map_url", label: "Walking Map URL" },
      { key: "map_destination", label: "Map Destination (for walk-from-here)" },
      { key: "meal_timing_note", label: "Meal Timing Note" },
      { key: "backup_plan", label: "Backup Plan" },
    ];

    const formHtml = fields
      .map((f) => {
        const val = item[f.key] != null ? String(item[f.key]) : "";
        const escaped = escapeHtml(val);
        if (f.type === "select") {
          const opts = f.options
            .map((o) => `<option value="${o}" ${(item[f.key] || "") === o ? "selected" : ""}>${o}</option>`)
            .join("");
          return `
            <div class="form-group">
              <label class="form-label">${f.label}</label>
              <select class="form-input edit-field" data-field="${f.key}">${opts}</select>
            </div>`;
        }
        if (f.type === "number") {
          return `
            <div class="form-group">
              <label class="form-label">${f.label}</label>
              <input class="form-input edit-field" type="number" data-field="${f.key}" value="${escaped}" min="0" />
            </div>`;
        }
        if (f.key === "time") {
          const timeMatch = val.match(/^(\d{1,2}:\d{2})\s*(AM|PM)/i);
          var hhmm = timeMatch ? timeMatch[1] : "";
          var period = timeMatch ? timeMatch[2].toUpperCase() : "AM";
          var amActive = period === "AM" ? " active" : "";
          var pmActive = period === "PM" ? " active" : "";
          return `
            <div class="form-group">
              <label class="form-label">${f.label}</label>
              <div class="time-input-group">
                <input class="form-input time-input-hhmm edit-field" type="text" data-field="${f.key}" value="${escapeHtml(hhmm)}" maxlength="5" placeholder="07:00" />
                <div class="ampm-toggle modal-ampm" data-time-field="${f.key}">
                  <button type="button" class="ampm-btn${amActive}" data-period="AM">AM</button>
                  <button type="button" class="ampm-btn${pmActive}" data-period="PM">PM</button>
                </div>
              </div>
            </div>`;
        }
        return `
          <div class="form-group">
            <label class="form-label">${f.label}</label>
            <input class="form-input edit-field" type="text" data-field="${f.key}" value="${escaped}" />
          </div>`;
      })
      .join("");

    showModal(
      "Edit Schedule Item",
      `<div>${formHtml}</div>`,
      async () => {
        const updates = {};
        $modalContainer.querySelectorAll(".edit-field").forEach((el) => {
          const key = el.dataset.field;
          let val = el.value;
          if (el.type === "number") val = val === "" ? null : Number(val);
          updates[key] = val;
        });

        // Validate time if it was edited
        if (updates.time) {
          var editTimeErr = validateTimeString(updates.time);
          if (editTimeErr) {
            showToast(editTimeErr, "error");
            return;
          }
        }

        // Reassemble time from HH:MM input + AM/PM toggle in modal
        var modalAmpm = $modalContainer.querySelector(".modal-ampm");
        if (modalAmpm && updates.time) {
          var activeBtn = modalAmpm.querySelector(".ampm-btn.active");
          var period = activeBtn ? activeBtn.dataset.period : "AM";
          updates.time = updates.time + " " + period;
        }

        try {
          const updated = await patchScheduleItem(planId, "update", index, { updates });
          updatePlanInStore(updated.plan_id, updated);
          navigateTo("plan-detail", { planId: updated.plan_id });
          showToast(t("toast.scheduleUpdated"), "success");
        } catch (err) {
          showToast(err.message, "error");
        }
      }
    );
  }

  async function removeScheduleItem(planId, index) {
    showConfirmModal(
      t("schedule.removeTitle"),
      t("schedule.removeConfirm"),
      async () => {
        try {
          const updated = await patchScheduleItem(planId, "remove", index);
          updatePlanInStore(updated.plan_id, updated);
          navigateTo("plan-detail", { planId: updated.plan_id });
          showToast(t("toast.scheduleRemoved"), "info");
        } catch (err) {
          showToast(err.message, "error");
        }
      }
    );
  }

  function openAddItemModal(planId) {
    const plan = planStore[planId];
    if (!plan) return;

    showModal(
      t("modal.addTitle"),
      `
      <div class="form-group">
        <label class="form-label">Time (HH:MM AM/PM)</label>
        <div class="time-input-group">
          <input class="form-input time-input-hhmm" id="add-time" type="text" maxlength="5" placeholder="07:00" />
          <div class="ampm-toggle modal-ampm-add">
            <button type="button" class="ampm-btn active" data-period="AM">AM</button>
            <button type="button" class="ampm-btn" data-period="PM">PM</button>
          </div>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Action</label>
        <input class="form-input" id="add-action" type="text" placeholder="Describe the activity..." />
      </div>
      <div class="form-group">
        <label class="form-label">Priority</label>
        <select class="form-input" id="add-priority">
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="low">Low</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Walking Time (min)</label>
        <input class="form-input" id="add-walk" type="number" min="0" placeholder="Optional" />
      </div>
      <div class="form-group">
        <label class="form-label">Wait Time (min)</label>
        <input class="form-input" id="add-wait" type="number" min="0" placeholder="Optional" />
      </div>
      <div class="form-group">
        <label class="form-label">Reminder Before (min)</label>
        <select class="form-input" id="add-reminder">
          <option value="">None</option>
          <option value="5">5 min</option>
          <option value="10">10 min</option>
          <option value="15">15 min</option>
          <option value="20">20 min</option>
          <option value="25">25 min</option>
          <option value="30">30 min</option>
          <option value="35">35 min</option>
          <option value="40">40 min</option>
          <option value="45">45 min</option>
          <option value="50">50 min</option>
          <option value="55">55 min</option>
          <option value="60">60 min</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Restaurant Recommendation</label>
        <input class="form-input" id="add-restaurant" type="text" placeholder="Optional" />
      </div>
      <div class="form-group">
        <label class="form-label">Backup Plan</label>
        <input class="form-input" id="add-backup" type="text" placeholder="Optional" />
      </div>
      `,
      async () => {
        var addTime = document.getElementById("add-time").value.trim();
        var addAmpm = $modalContainer.querySelector(".modal-ampm-add");
        if (addAmpm && addTime) {
          var activeBtn = addAmpm.querySelector(".ampm-btn.active");
          var period = activeBtn ? activeBtn.dataset.period : "AM";
          addTime = addTime + " " + period;
        }
        const scheduleItem = {
          time: addTime,
          action: document.getElementById("add-action").value.trim(),
          priority: document.getElementById("add-priority").value,
          walking_time_min: parseOrNull(document.getElementById("add-walk").value),
          wait_time_min: parseOrNull(document.getElementById("add-wait").value),
          reminder_min: parseOrNull(document.getElementById("add-reminder").value),
          restaurant: document.getElementById("add-restaurant").value.trim() || null,
          backup_plan: document.getElementById("add-backup").value.trim() || null,
        };

        if (!scheduleItem.time || !scheduleItem.action) {
          showToast(t("error.timeRequired"), "error");
          return;
        }

        // Validate the time format (HH:MM, 1-12 hours, 0-59 minutes)
        var timeStrErr = validateTimeString(addTime);
        if (timeStrErr) {
          showToast(timeStrErr, "error");
          return;
        }

        const position = Array.isArray(plan.schedule) ? plan.schedule.length : 0;

        try {
          const updated = await patchScheduleItem(planId, "add", position, { schedule_item: scheduleItem });
          updatePlanInStore(updated.plan_id, updated);
          navigateTo("plan-detail", { planId: updated.plan_id });
          showToast(t("toast.scheduleAdded"), "success");
        } catch (err) {
          showToast(err.message, "error");
        }
      }
    );
  }

  function parseOrNull(val) {
    const trimmed = String(val).trim();
    if (trimmed === "") return null;
    const n = Number(trimmed);
    return Number.isNaN(n) ? null : n;
  }

  /* ------------------------------------------------------------------------
     AM/PM Toggle
     ------------------------------------------------------------------------ */
  function getSelectedPeriod() {
    if (!$tripDepartureAmpm) return "AM";
    var active = $tripDepartureAmpm.querySelector(".ampm-btn.active");
    return active ? active.dataset.period : "AM";
  }

  function resetAmpmToggle() {
    if (!$tripDepartureAmpm) return;
    var buttons = $tripDepartureAmpm.querySelectorAll(".ampm-btn");
    buttons.forEach(function (btn) {
      btn.classList.toggle("active", btn.dataset.period === "AM");
    });
  }

  /* ------------------------------------------------------------------------
     Mobile Sidebar State
     ------------------------------------------------------------------------ */
  function closeMobileSidebar() {
    $sidebar.classList.remove("open");
    if ($sidebarOverlay) $sidebarOverlay.classList.remove("open");
    $mobileMenuBtn.innerHTML = "&#9776;";
    document.body.style.overflow = "";
  }

  function openMobileSidebar() {
    $sidebar.classList.add("open");
    if ($sidebarOverlay) $sidebarOverlay.classList.add("open");
    $mobileMenuBtn.innerHTML = "&#10005;";
    document.body.style.overflow = "hidden";
  }

  /* ------------------------------------------------------------------------
     Event Binding
     ------------------------------------------------------------------------ */
  function bindEvents() {
    // Departure time: auto-advance from hours to minutes when user types colon,
    // and from minutes back to hours when Backspace is pressed on an empty field.
    if ($tripDepartureHh && $tripDepartureMm) {
      $tripDepartureHh.addEventListener("keydown", function (e) {
        if (e.key === ":" || e.key === ";") {
          e.preventDefault();
          // Move colon to minutes field conceptually — just advance focus
          $tripDepartureMm.focus();
          $tripDepartureMm.select();
        }
        // Auto-advance when 2 digits are typed (keydown fires before char insertion,
        // so check >= 1 meaning the incoming key will be the 2nd digit)
        if ($tripDepartureHh.value.length >= 1 && e.key !== "Backspace" && e.key !== "Delete" && e.key !== ":" && e.key !== ";") {
          // Let the character type, then advance
          setTimeout(function () {
            if ($tripDepartureHh.value.length >= 2) {
              $tripDepartureMm.focus();
              $tripDepartureMm.select();
            }
          }, 10);
        }
      });
      $tripDepartureMm.addEventListener("keydown", function (e) {
        if ((e.key === "Backspace" || e.key === "Delete") && $tripDepartureMm.value === "") {
          e.preventDefault();
          $tripDepartureHh.focus();
          $tripDepartureHh.select();
        }
      });
      // Auto-advance minutes to AM/PM area when 2 digits are typed
      $tripDepartureMm.addEventListener("input", function () {
        if ($tripDepartureMm.value.length >= 2 && $tripDepartureAmpm) {
          var firstBtn = $tripDepartureAmpm.querySelector(".ampm-btn");
          if (firstBtn) firstBtn.focus();
        }
      });
      // Allow only digits in time fields
      [$tripDepartureHh, $tripDepartureMm].forEach(function (el) {
        el.addEventListener("input", function () {
          el.value = el.value.replace(/[^0-9]/g, "");
        });
      });
      // Clamp hours to 1-12 and minutes to 0-59 on blur
      $tripDepartureHh.addEventListener("blur", function () {
        var v = parseInt($tripDepartureHh.value, 10);
        if ($tripDepartureHh.value !== "" && (isNaN(v) || v < 1)) $tripDepartureHh.value = "1";
        else if (v > 12) $tripDepartureHh.value = "12";
        if ($tripDepartureHh.value.length === 1 && $tripDepartureHh.value !== "") {
          $tripDepartureHh.value = "0" + $tripDepartureHh.value;
        }
      });
      $tripDepartureMm.addEventListener("blur", function () {
        var v = parseInt($tripDepartureMm.value, 10);
        if ($tripDepartureMm.value !== "" && (isNaN(v) || v < 0)) $tripDepartureMm.value = "00";
        else if (v > 59) $tripDepartureMm.value = "59";
        if ($tripDepartureMm.value.length === 1 && $tripDepartureMm.value !== "") {
          $tripDepartureMm.value = "0" + $tripDepartureMm.value;
        }
      });
    }

    // AM/PM toggle buttons (homepage departure field)
    if ($tripDepartureAmpm) {
      $tripDepartureAmpm.addEventListener("click", function (e) {
        var btn = e.target.closest(".ampm-btn");
        if (!btn) return;
        var buttons = $tripDepartureAmpm.querySelectorAll(".ampm-btn");
        buttons.forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
      });
    }

    // AM/PM toggle buttons inside modals (delegated)
    $modalContainer.addEventListener("click", function (e) {
      var btn = e.target.closest(".ampm-btn");
      if (!btn) return;
      var toggle = btn.closest(".ampm-toggle");
      if (!toggle) return;
      var buttons = toggle.querySelectorAll(".ampm-btn");
      buttons.forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
    });

    // Navigation
    $$(".nav-item[data-page]").forEach((el) => {
      el.addEventListener("click", () => navigateTo(el.dataset.page));
    });

    // Sidebar saved plan clicks (delegated)
    $sidebarSavedPlans.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-action='open-plan']");
      if (btn && btn.dataset.planId) {
        navigateTo("plan-detail", { planId: btn.dataset.planId });
      }
    });

    // Plans list clicks (delegated)
    $plansList.addEventListener("click", (e) => {
      const card = e.target.closest("[data-action='open-plan']");
      if (card && card.dataset.planId) {
        navigateTo("plan-detail", { planId: card.dataset.planId });
      }
    });

    // Plan detail content delegation for schedule editing & delete
    $planDetailContent.addEventListener("click", (e) => {
      handleScheduleUiClick(e);

      const editBtn = e.target.closest(".edit-schedule-btn");
      const removeBtn = e.target.closest(".remove-schedule-btn");
      const addBtn = e.target.closest("#btn-add-schedule-item");

      if (editBtn && currentPlanId) {
        const idx = parseInt(editBtn.dataset.index, 10);
        const plan = planStore[currentPlanId];
        if (plan && Array.isArray(plan.schedule) && plan.schedule[idx]) {
          openEditModal(currentPlanId, plan.schedule[idx], idx);
        }
      }

      if (removeBtn && currentPlanId) {
        const idx = parseInt(removeBtn.dataset.index, 10);
        removeScheduleItem(currentPlanId, idx);
      }

      if (addBtn && currentPlanId) {
        openAddItemModal(currentPlanId);
      }
    });

    // Inline new-trip result: expand + map actions
    $resultNewTrip.addEventListener("click", function (e) {
      handleScheduleUiClick(e);
    });

    // Reminder dropdown change (plan detail)
    $planDetailContent.addEventListener("change", function (e) {
      var sel = e.target.closest(".reminder-inline");
      if (sel && currentPlanId) {
        var idx = parseInt(sel.dataset.scheduleIndex, 10);
        var val = sel.value === "" ? null : parseInt(sel.value, 10);
        onReminderChange(currentPlanId, idx, val);
      }
    });

    // Reminder dropdown change (inline result on new trip page)
    $resultNewTrip.addEventListener("change", function (e) {
      var sel = e.target.closest(".reminder-inline");
      if (sel) {
        var planId = sel.dataset.planId;
        var idx = parseInt(sel.dataset.scheduleIndex, 10);
        var val = sel.value === "" ? null : parseInt(sel.value, 10);
        if (planId) {
          onReminderChange(planId, idx, val);
        }
      }
    });

    // Back button on plan detail page
    const backBtn = $("#btn-back-plans");
    if (backBtn) {
      backBtn.addEventListener("click", () => navigateTo("my-plans"));
    }

    // Generate button
    $btnGenerate.addEventListener("click", generateTrip);

    // Enter key in textareas triggers generate
    $tripInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        generateTrip();
      }
    });

    // Clear store
    $clearBtn.addEventListener("click", () => {
      showConfirmModal(
        t("confirm.clearTitle"),
        t("confirm.clearMessage"),
        () => {
          clearPlanStore();
          showToast(t("toast.allPlansCleared"), "info");
          if (currentPage === "plan-detail") {
            navigateTo("my-plans");
          }
        }
      );
    });

    // Mobile menu toggle
    $mobileMenuBtn.addEventListener("click", () => {
      if ($sidebar.classList.contains("open")) {
        closeMobileSidebar();
      } else {
        openMobileSidebar();
      }
    });

    // Close sidebar on overlay click (mobile)
    if ($sidebarOverlay) {
      $sidebarOverlay.addEventListener("click", () => {
        closeMobileSidebar();
      });
    }

    // Close sidebar on outside click (mobile) — fallback for when overlay isn't rendered
    document.addEventListener("click", (e) => {
      if (
        window.innerWidth <= 768 &&
        $sidebar.classList.contains("open") &&
        !$sidebar.contains(e.target) &&
        e.target !== $mobileMenuBtn &&
        !$mobileMenuBtn.contains(e.target)
      ) {
        closeMobileSidebar();
      }
    });

    // Close sidebar on Escape key
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && $sidebar.classList.contains("open")) {
        closeMobileSidebar();
      }
    });

    // Close sidebar on window resize above breakpoint
    window.addEventListener("resize", () => {
      if (window.innerWidth > 768 && $sidebar.classList.contains("open")) {
        closeMobileSidebar();
      }
    });

    // Language selector
    var $langSelector = $("#lang-selector");
    if ($langSelector) {
      $langSelector.value = getCurrentLang();
      $langSelector.addEventListener("change", function () {
        setLang(this.value, function () {
          // Refresh all dynamic UI after language change
          refreshDynamicUI();
        });
      });
    }

    // Bug report button
    var $bugBtn = $("#btn-bug-report");
    if ($bugBtn) {
      $bugBtn.addEventListener("click", function () {
        if (window.BugDrop && typeof window.BugDrop.open === "function") {
          window.BugDrop.open();
          return;
        }
        openBugReport();
      });
    }
  }

  /* ------------------------------------------------------------------------
     Toast Notifications
     ------------------------------------------------------------------------ */
  function showToast(message, type) {
    type = type || "info";
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    $toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-10px)";
      toast.style.transition = "opacity 0.3s ease, transform 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  /* ------------------------------------------------------------------------
     Modals
     ------------------------------------------------------------------------ */
  function showModal(title, bodyHtml, onConfirm) {
    $modalContainer.innerHTML = `
      <div class="modal-backdrop" id="modal-backdrop">
        <div class="modal" data-bugdrop-mask>
          <div class="modal-title">${escapeHtml(title)}</div>
          <div class="modal-body">${bodyHtml}</div>
          <div class="modal-footer">
            <button class="btn btn-secondary" id="modal-cancel">Cancel</button>
            <button class="btn btn-primary" id="modal-confirm">Confirm</button>
          </div>
        </div>
      </div>
    `;

    const closeModal = () => {
      $modalContainer.innerHTML = "";
    };

    document.getElementById("modal-cancel").addEventListener("click", closeModal);
    document.getElementById("modal-backdrop").addEventListener("click", (e) => {
      if (e.target === e.currentTarget) closeModal();
    });
    document.addEventListener("keydown", function escHandler(e) {
      if (e.key === "Escape") {
        closeModal();
        document.removeEventListener("keydown", escHandler);
      }
    });

    document.getElementById("modal-confirm").addEventListener("click", async () => {
      await onConfirm();
      closeModal();
    });
  }

  function showConfirmModal(title, message, onConfirm) {
    showModal(
      title,
      `<p class="text-sm text-secondary">${escapeHtml(message)}</p>`,
      onConfirm
    );
  }

  /* ------------------------------------------------------------------------
     Inline Reminder Handler
     ------------------------------------------------------------------------ */
  async function onReminderChange(planId, index, value) {
    try {
      var updates = { reminder_min: value };
      var updated = await patchScheduleItem(planId, "update", index, { updates: updates });
      updatePlanInStore(updated.plan_id, updated);
      showToast(value ? t("toast.reminderSet", { min: value }) : t("toast.reminderRemoved"), "success");
      navigateTo("plan-detail", { planId: updated.plan_id });
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  /* ------------------------------------------------------------------------
     Utilities
     ------------------------------------------------------------------------ */
  function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  function escapeHtml(str) {
    if (str == null) return "";
    var amp = "&" + "amp;";
    var lt = "&" + "lt;";
    var gt = "&" + "gt;";
    var quot = "&" + "quot;";
    var apos = "&" + "#039;";
    return String(str)
      .replace(/&/g, amp)
      .replace(/</g, lt)
      .replace(/>/g, gt)
      .replace(/"/g, quot)
      .replace(/'/g, apos);
  }

  /* ------------------------------------------------------------------------
     City-State Validation
     ------------------------------------------------------------------------ */

  // State patterns — supports both 2-letter codes (FL) and spelled-out
  // names (Florida) so users aren't forced into one specific format.
  var _stateCodePattern = /\b(A[LKZR]|C[AOT]|D[EC]|F[LM]|G[AU]|HI|I[DLNA]|K[SY]|LA|M[ADEHINOPST]|N[CDEHJMVY]|O[HKR]|P[AWR]|RI|S[CD]|T[NX]|UT|V[AIT]|W[AIVY])\b/i;

  var _fullStateNames = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
    "District of Columbia", "Puerto Rico", "Guam", "U.S. Virgin Islands"
  ];

  // Build a single regex that matches any spelled-out state name (case-insensitive)
  var _fullStatePattern = new RegExp(
    "\\b(?:" + _fullStateNames
      .map(function(n) { return n.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'); })
      .join("|") +
    ")\\b",
    "i"
  );

  function _hasStateIndicator(text) {
    return _stateCodePattern.test(text) || _fullStatePattern.test(text);
  }

  function validateCityState(input) {
    if (!input) return null;

    // List of common U.S. city names that exist in multiple states.
    // When these are mentioned without a state abbreviation or full
    // state name, users must be prompted to specify which state.
    var ambiguousCities = {
      "jacksonville": true,
      "portland": true,
      "springfield": true,
      "columbus": true,
      "franklin": true,
      "greenville": true,
      "salem": true,
      "arlington": true,
      "richmond": true,
      "aurora": true,
      "fairview": true,
      "madison": true,
      "georgetown": true,
      "clinton": true,
      "bloomington": true,
      "rochester": true,
      "lexington": true,
      "cleveland": true,
      "dover": true,
      "newark": true,
      "manchester": true,
      "atlanta": true,
      "birmingham": true,
      "montgomery": true,
      "lafayette": true,
      "alexandria": true,
      "lancaster": true,
      "kingston": true,
      "newport": true,
      "charleston": true,
      "bowling green": true,
      "port charlotte": true,
      "warren": true,
      "oxford": true,
      "pasadena": true,
      "bellevue": true,
      "dublin": true,
      "charleston": true,
    };

    // Find city names in the input that match our ambiguous list
    var lower = input.toLowerCase();
    var foundCities = [];

    for (var city in ambiguousCities) {
      if (ambiguousCities.hasOwnProperty(city)) {
        // Check for whole-word match of the city name
        var re = new RegExp("\\b" + city.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&') + "\\b", "i");
        if (re.test(lower)) {
          foundCities.push(city);
        }
      }
    }

    if (foundCities.length === 0) return null;

    // Check if a state abbreviation OR full state name is present
    var hasState = _hasStateIndicator(input);

    if (!hasState) {
      var cityLabel = foundCities[0].replace(/\b\w/g, function(c) { return c.toUpperCase(); });
      return t("city.multipleStates", { city: cityLabel });
    }

    return null;
  }

  /* ------------------------------------------------------------------------
     Address Validation
     ------------------------------------------------------------------------ */
  function validateAddress(addr) {
    if (!addr) return null; // empty is fine (field is optional)

    // Must contain a street number (digits at start or after a comma)
    var hasStreet = /\d+\s+\w+/i.test(addr);
    // Must contain a city-like component followed by comma/space and
    // either a US state abbreviation OR a spelled-out state name
    var hasCityState = /[a-z]+(?:,\s*|\s+)(A[LKZR]|C[AOT]|D[EC]|F[LM]|G[AU]|HI|I[DLNA]|K[SY]|LA|M[ADEHINOPST]|N[CDEHJMVY]|O[HKR]|P[AWR]|RI|S[CD]|T[NX]|UT|V[AIT]|W[AIVY])\b/i.test(addr) || _fullStatePattern.test(addr);
    // Must contain a 5-digit ZIP code (optionally with +4)
    var hasZip = /\b\d{5}(?:-\d{4})?\b/.test(addr);

    var missing = [];
    if (!hasStreet) missing.push("street address");
    if (!hasCityState) missing.push("city and state");
    if (!hasZip) missing.push("zip code");

    if (missing.length === 0) return null;

    if (missing.length === 3) {
      return t("error.missingFullAddress");
    }

    // Single missing field — give a specific hint
    if (missing.length === 1) {
      if (missing[0] === "street address") {
        return t("error.missingStreet");
      }
      if (missing[0] === "city and state") {
        return t("error.missingCityState");
      }
      if (missing[0] === "zip code") {
        return t("error.missingZip");
      }
    }

    // Two missing fields
    if (missing[0] === "city and state" || missing[1] === "city and state") {
      return t("error.missingCityState2");
    }
    return t("error.missingGeneric");
  }

  /* ------------------------------------------------------------------------
     Time Validation
     ------------------------------------------------------------------------ */

  /**
   * Validate a 12-hour time entry (HH:MM with AM/PM).
   * Returns null if valid, or an error message string if invalid.
   */
  function validateTimeInput(hh, mm) {
    if (!hh && !mm) return null; // empty is fine — time is optional
    var hours = parseInt(hh, 10);
    var minutes = parseInt(mm, 10);
    if (isNaN(hours) || isNaN(minutes)) return t("error.validTime");
    if (hours < 1 || hours > 12) return t("error.hourRange");
    if (minutes < 0 || minutes > 59) return t("error.minuteRange");
    return null;
  }

  /**
   * Validate a time string in HH:MM format (used in modals).
   * Returns null if valid, or an error message string if invalid.
   */
  function validateTimeString(timeStr) {
    if (!timeStr) return null; // empty is fine
    var match = timeStr.match(/^(\d{1,2}):(\d{2})$/);
    if (!match) return t("error.timeFormat");
    var hours = parseInt(match[1], 10);
    var minutes = parseInt(match[2], 10);
    if (hours < 1 || hours > 12) return t("error.hourRange12");
    if (minutes < 0 || minutes > 59) return t("error.minuteRange");
    return null;
  }

  /* ------------------------------------------------------------------------
     Client Error Ring Buffer (for bug reporter diagnostics)
     ------------------------------------------------------------------------ */

  var _errorLog = [];
  var MAX_ERROR_LOG = 15;

  // Capture uncaught errors and console.error calls
  window.addEventListener("error", function (e) {
    var msg = e.message || String(e.error || "");
    if (msg && _errorLog.length < MAX_ERROR_LOG * 2) {
      _errorLog.push("[uncaught] " + msg.slice(0, 200));
      if (_errorLog.length > MAX_ERROR_LOG) _errorLog.shift();
    }
  });

  // Intercept console.error for diagnostics
  var _origConsoleError = console.error;
  console.error = function () {
    var args = Array.prototype.slice.call(arguments);
    var msg = args.map(function (a) { return typeof a === "string" ? a : JSON.stringify(a).slice(0, 150); }).join(" ");
    if (msg && _errorLog.length < MAX_ERROR_LOG * 2) {
      _errorLog.push("[console] " + msg.slice(0, 200));
      if (_errorLog.length > MAX_ERROR_LOG) _errorLog.shift();
    }
    return _origConsoleError.apply(console, args);
  };

  function recentErrorLogs() {
    return _errorLog.slice(-MAX_ERROR_LOG);
  }

  /* ------------------------------------------------------------------------
  Bug Reporter fallback — pre-fills a GitHub issue on jssturm/Plan-It
  ------------------------------------------------------------------------ */

  /**
   * Build a GitHub issue URL with title/body/labels pre-filled.
   * The user reviews the payload in a modal and clicks to open GitHub.
   * Nothing is sent to any server until the user clicks "Open GitHub issue".
   */
  function buildBugReportUrl(description) {
    var desc = (description || "").trim();
    var title = desc ? desc.replace(/\s+/g, " ").trim().slice(0, 80) : "bug report";
    var scrubbedDesc = desc.replace(/(sk|key|token|secret|bearer|api[-_]?key)([-_=:\s"']+)[A-Za-z0-9._-]{8,}/gi, "$1$2[redacted]");

    var bodyLines = [
      t("bug.whatHappened"),
      scrubbedDesc || "_(describe what you were doing and what went wrong)_",
      "",
      t("bug.envLabel"),
      "- **URL:** `" + (window.location.pathname + window.location.search).slice(0, 200) + "`",
      "- **Browser:** " + (navigator.userAgent || "?").slice(0, 200),
      "- **Viewport:** " + window.innerWidth + "\u00D7" + window.innerHeight,
      "- **Screen:** " + window.screen.width + "\u00D7" + window.screen.height,
      "",
      "## Recent errors",
      recentErrorLogs().length ? "```\n" + recentErrorLogs().join("\n") + "\n```" : "_(none captured)_",
      "",
      "---",
      t("bug.filedFrom"),
    ];

    var body = bodyLines.join("\n").slice(0, 4000);
    var params = new URLSearchParams({
      title: title,
      body: body,
      labels: "bug,web-alpha",
    });

    return "https://github.com/jssturm/Plan-It/issues/new?" + params.toString();
  }

  /**
   * Build the preview payload string shown in the modal expandable section.
   */
  function buildBugReportPreview(description) {
    var desc = (description || "").trim();
    var scrubbedDesc = desc.replace(/(sk|key|token|secret|bearer|api[-_]?key)([-_=:\s"']+)[A-Za-z0-9._-]{8,}/gi, "$1$2[redacted]");

    return [
      t("bug.previewTitle"),
      "",
      t("bug.envLabel"),
      "URL: " + (window.location.pathname + window.location.search).slice(0, 200),
      "Browser: " + (navigator.userAgent || "?").slice(0, 200),
      "Viewport: " + window.innerWidth + "x" + window.innerHeight,
      "",
      "What happened:",
      scrubbedDesc || "(describe what you were doing)",
      "",
      "Recent errors: " + (recentErrorLogs().length || "none"),
    ].join("\n");
  }

  /**
   * Open the bug report modal.
   */
  function openBugReport() {
    var desc = "";
    var previewOpen = false;

    var bodyHtml =
      '<textarea id="bug-desc" class="form-textarea" rows="4" autofocus placeholder="' + t("bug.placeholder") + '" style="resize:vertical;min-height:90px;"></textarea>' +
      '<details id="bug-preview-details" class="mt-3">' +
        '<summary class="cursor-pointer select-none px-3 py-2 text-xs font-medium text-muted" style="cursor:pointer;">' + t("bug.previewLabel") + '</summary>' +
        '<pre id="bug-preview-content" class="bug-modal-preview">' + buildBugReportPreview("") + '</pre>' +
      '</details>' +
      '<p class="bug-modal-privacy">' +
        '<span class="bug-modal-privacy-icon">\uD83D\uDD12</span>' +
        '<span>' + t("bug.privacy") + '</span>' +
      '</p>';

    showModal(
      t("bug.title"),
      bodyHtml,
      function () {
        // This is the confirm callback — but we override it below
      }
    );

    // Override the modal footer to use a link instead of a button for "Open GitHub issue"
    var footer = $modalContainer.querySelector(".modal-footer");
    if (footer) {
      var cancelBtn = footer.querySelector("#modal-cancel");
      var confirmBtn = footer.querySelector("#modal-confirm");

      // Replace confirm button with an anchor
      if (confirmBtn) {
        var descEl = $modalContainer.querySelector("#bug-desc");
        var updateIssueUrl = function () {
          desc = descEl ? descEl.value : "";
          var url = buildBugReportUrl(desc);
          var link = footer.querySelector("#bug-issue-link");
          if (link) link.href = url;
          // Update preview
          var preview = $modalContainer.querySelector("#bug-preview-content");
          if (preview) preview.textContent = buildBugReportPreview(desc);
        };

        // Replace the confirm button with an anchor element
        var link = document.createElement("a");
        link.id = "bug-issue-link";
        link.className = "btn btn-primary";
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.href = buildBugReportUrl("");
        link.innerHTML = t("bug.openIssue");
        link.addEventListener("click", function () {
          // Close modal after opening the issue
          $modalContainer.innerHTML = "";
        });

        confirmBtn.parentNode.replaceChild(link, confirmBtn);

        // Update URL and preview as user types
        if (descEl) {
          descEl.addEventListener("input", updateIssueUrl);
          // Also update when preview details toggle
          var details = $modalContainer.querySelector("#bug-preview-details");
          if (details) {
            details.addEventListener("toggle", function () {
              if (details.open && !previewOpen) {
                previewOpen = true;
                updateIssueUrl();
              }
            });
          }
        }
      }
    }
  }

  /* ------------------------------------------------------------------------
     Dynamic UI Refresh (called after language switch)
     ------------------------------------------------------------------------ */

  /**
   * Re-render all dynamic content after language change.
   * Called by the language selector change handler.
   */
  function refreshDynamicUI() {
    // Refresh topbar title based on current page
    var titles = {
      "new-trip": t("topbar.newTrip"),
      "my-plans": t("topbar.myPlans"),
      "plan-detail": t("topbar.itinerary"),
    };
    $topbarTitle.textContent = titles[currentPage] || "Plan-It";

    // Refresh sidebar saved plans section
    renderSidebarSavedPlans();

    // Refresh health label
    if ($healthDot.className.indexOf("online") >= 0) {
      $healthLabel.textContent = t("health.online");
    } else {
      $healthLabel.textContent = t("health.unreachable");
    }

    // Re-run i18nInit for any remaining data-i18n attributes in dynamic content
    if (window.i18nInit) window.i18nInit();

    // Refresh current page
    if (currentPage === "my-plans") {
      renderPlansList();
    } else if (currentPage === "plan-detail" && currentPlanId) {
      renderPlanDetail(currentPlanId);
    } else if (currentPage === "new-trip") {
      // Refresh the generate button text
      if (!$btnGenerate.disabled) {
        $btnGenerate.innerHTML = t("newTrip.generate");
      }
      // Refresh result area if visible
      if (!$resultNewTrip.classList.contains("hidden") && currentPlanId && planStore[currentPlanId]) {
        renderPlanResultInline(planStore[currentPlanId]);
      }
    }
  }

  /* ------------------------------------------------------------------------
     Bootstrap
     ------------------------------------------------------------------------ */
  document.addEventListener("DOMContentLoaded", init);
})();