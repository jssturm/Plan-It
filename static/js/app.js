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
    var parsed = parseFlexibleTimeString(timeStr, "AM");
    if (!parsed) return null;
    var hours = parseInt(parsed.hh, 10);
    var mins = parseInt(parsed.mm, 10);
    if (parsed.period === "PM" && hours < 12) hours += 12;
    if (parsed.period === "AM" && hours === 12) hours = 0;
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

    const startRaw = $tripStart.value.trim();
    // Soft-normalize free-form US addresses (commas optional) without blocking.
    const start = startRaw ? normalizeUSAddress(startRaw) : "";
    if (start && start !== startRaw && $tripStart) {
      $tripStart.value = start;
    }
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
        // Extract a valid time from whatever the user typed (08 + blank,
        // compact 0800, 8am, etc.) instead of hard-failing into a toast loop.
        var parsedDep = parseFlexibleDeparture(hh, mm, departurePeriod);
        if (!parsedDep) {
          showToast(t("error.validTime"), "error");
          $btnGenerate.disabled = false;
          $btnGenerate.innerHTML = "&#128640; Generate Itinerary";
          return;
        }
        // Reflect the normalized values back into the fields
        if ($tripDepartureHh) $tripDepartureHh.value = parsedDep.hh;
        if ($tripDepartureMm) $tripDepartureMm.value = parsedDep.mm;
        if ($tripDepartureAmpm) {
          var buttons = $tripDepartureAmpm.querySelectorAll(".ampm-btn");
          buttons.forEach(function (b) {
            b.classList.toggle("active", b.dataset.period === parsedDep.period);
          });
        }
        departure = parsedDep.hh + ":" + parsedDep.mm + " " + parsedDep.period;
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
        if (item.walking_map_url) {
          metaBadges.push(
            '<a href="' + escapeHtml(item.walking_map_url) + '" target="_blank" rel="noopener" class="badge badge-walk-map" title="' + t("schedule.walkToHere") + '">' + t("schedule.walkToHere") + '</a>'
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
                var sel = currentReminder === v ? " selected" : "";
                return '<option value="' + v + '"' + sel + '>' + label + '</option>';
              }).join("")
            + '</select>';

        return `
          <div class="timeline-item" data-schedule-index="${idx}">
            <div class="timeline-dot ${prioClass}"></div>
            <div class="flex items-center gap-2">
              <span class="timeline-time">${escapeHtml(item.time || "—")}</span>
              ${editControls}
            </div>
            <div class="timeline-action">${escapeHtml(item.action)}</div>
            ${item.meal_timing_note ? `<div class="text-xs text-muted mb-2">&#128161; ${escapeHtml(item.meal_timing_note)}</div>` : ""}
            <div class="timeline-meta">${reminderSelect}${metaBadges.join("")}</div>
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
        </div>
        <div class="card">
          <div class="timeline" id="schedule-timeline">${items}</div>
          ${addBtn}
        </div>
      </div>
    `;
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
                <input class="form-input time-input-hhmm edit-field" type="text" data-field="${f.key}" value="${escapeHtml(hhmm)}" maxlength="12" placeholder="07:00" />
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

        // Normalize free-form time (0800, 8:00, 8am, etc.) then reassemble with AM/PM
        if (updates.time) {
          var modalAmpmEdit = $modalContainer.querySelector(".modal-ampm");
          var editPeriod = "AM";
          if (modalAmpmEdit) {
            var editActive = modalAmpmEdit.querySelector(".ampm-btn.active");
            editPeriod = editActive ? editActive.dataset.period : "AM";
          }
          var parsedEdit = parseFlexibleTimeString(updates.time, editPeriod);
          if (!parsedEdit) {
            showToast(t("error.validTime"), "error");
            return;
          }
          updates.time = parsedEdit.hh + ":" + parsedEdit.mm + " " + parsedEdit.period;
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
          <input class="form-input time-input-hhmm" id="add-time" type="text" maxlength="12" placeholder="07:00" />
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
        var addTimeRaw = document.getElementById("add-time").value.trim();
        var addAction = document.getElementById("add-action").value.trim();
        if (!addTimeRaw || !addAction) {
          showToast(t("error.timeRequired"), "error");
          return;
        }

        var addAmpmEl = $modalContainer.querySelector(".modal-ampm-add");
        var addPeriod = "AM";
        if (addAmpmEl) {
          var addActive = addAmpmEl.querySelector(".ampm-btn.active");
          addPeriod = addActive ? addActive.dataset.period : "AM";
        }
        var parsedAdd = parseFlexibleTimeString(addTimeRaw, addPeriod);
        if (!parsedAdd) {
          showToast(t("error.validTime"), "error");
          return;
        }

        const scheduleItem = {
          time: parsedAdd.hh + ":" + parsedAdd.mm + " " + parsedAdd.period,
          action: addAction,
          priority: document.getElementById("add-priority").value,
          walking_time_min: parseOrNull(document.getElementById("add-walk").value),
          wait_time_min: parseOrNull(document.getElementById("add-wait").value),
          reminder_min: parseOrNull(document.getElementById("add-reminder").value),
          restaurant: document.getElementById("add-restaurant").value.trim() || null,
          backup_plan: document.getElementById("add-backup").value.trim() || null,
        };

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
      // Allow digits in time fields; if a compact HHmm is typed/pasted into hours,
      // split it across HH + MM so "0800" becomes 08:00 instead of erroring.
      [$tripDepartureHh, $tripDepartureMm].forEach(function (el) {
        el.addEventListener("input", function () {
          el.value = el.value.replace(/[^0-9]/g, "");
          if (el === $tripDepartureHh && el.value.length >= 3) {
            var compact = parseFlexibleTimeString(el.value, getSelectedPeriod());
            if (compact) {
              $tripDepartureHh.value = compact.hh;
              $tripDepartureMm.value = compact.mm;
              if ($tripDepartureAmpm) {
                $tripDepartureAmpm.querySelectorAll(".ampm-btn").forEach(function (b) {
                  b.classList.toggle("active", b.dataset.period === compact.period);
                });
              }
              $tripDepartureMm.focus();
            }
          }
        });
      });
      $tripDepartureHh.addEventListener("paste", function (e) {
        var text = (e.clipboardData || window.clipboardData).getData("text") || "";
        var parsed = parseFlexibleTimeString(text.trim(), getSelectedPeriod());
        if (parsed) {
          e.preventDefault();
          $tripDepartureHh.value = parsed.hh;
          $tripDepartureMm.value = parsed.mm;
          if ($tripDepartureAmpm) {
            $tripDepartureAmpm.querySelectorAll(".ampm-btn").forEach(function (b) {
              b.classList.toggle("active", b.dataset.period === parsed.period);
            });
          }
        }
      });
      // Clamp hours to 1-12 and minutes to 0-59 on blur (after compact split)
      $tripDepartureHh.addEventListener("blur", function () {
        if ($tripDepartureHh.value.length >= 3) {
          var compactBlur = parseFlexibleTimeString($tripDepartureHh.value, getSelectedPeriod());
          if (compactBlur) {
            $tripDepartureHh.value = compactBlur.hh;
            if (!$tripDepartureMm.value) $tripDepartureMm.value = compactBlur.mm;
            return;
          }
        }
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
      const editBtn = e.target.closest(".edit-schedule-btn");
      const removeBtn = e.target.closest(".remove-schedule-btn");
      const addBtn = e.target.closest("#btn-add-schedule-item");
      const deleteBtn = e.target.closest("#btn-delete-plan");

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
      $bugBtn.addEventListener("click", openBugReport);
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
        <div class="modal">
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
     Address Normalization (graceful — never blocks submit)
     ------------------------------------------------------------------------ */

  var _US_STATE_NAMES = {
    alabama: "AL", alaska: "AK", arizona: "AZ", arkansas: "AR", california: "CA",
    colorado: "CO", connecticut: "CT", delaware: "DE", florida: "FL", georgia: "GA",
    hawaii: "HI", idaho: "ID", illinois: "IL", indiana: "IN", iowa: "IA",
    kansas: "KS", kentucky: "KY", louisiana: "LA", maine: "ME", maryland: "MD",
    massachusetts: "MA", michigan: "MI", minnesota: "MN", mississippi: "MS",
    missouri: "MO", montana: "MT", nebraska: "NE", nevada: "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", ohio: "OH", oklahoma: "OK",
    oregon: "OR", pennsylvania: "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", tennessee: "TN", texas: "TX", utah: "UT", vermont: "VT",
    virginia: "VA", washington: "WA", "west virginia": "WV", wisconsin: "WI",
    wyoming: "WY", "district of columbia": "DC", "washington dc": "DC", dc: "DC"
  };

  /**
   * Soft-normalize a free-form US address into "street, city, ST ZIP" when
   * components can be inferred. Never rejects — returns original trim on failure.
   */
  function normalizeUSAddress(raw) {
    if (!raw || !String(raw).trim()) return raw;
    var text = String(raw).trim().replace(/;/g, ",").replace(/\s+/g, " ");
    var zip = "";
    var zipMatch = text.match(/\b(\d{5}(?:-\d{4})?)\b/);
    if (zipMatch) {
      zip = zipMatch[1];
      text = (text.slice(0, zipMatch.index) + " " + text.slice(zipMatch.index + zipMatch[0].length))
        .trim().replace(/^,|,$/g, "").trim();
    }

    var state = "";
    var lower = text.toLowerCase();
    var bestLen = 0;
    Object.keys(_US_STATE_NAMES).forEach(function (name) {
      var re = new RegExp("\\b" + name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "i");
      if (re.test(lower) && name.length > bestLen) {
        bestLen = name.length;
        state = _US_STATE_NAMES[name];
      }
    });
    if (state && bestLen > 2) {
      var matchedName = Object.keys(_US_STATE_NAMES).filter(function (n) {
        return _US_STATE_NAMES[n] === state && n.length === bestLen;
      })[0];
      var nameRe = new RegExp("\\b" + matchedName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "i");
      text = text.replace(nameRe, " ").replace(/\s{2,}/g, " ").trim().replace(/^,|,$/g, "").trim();
    } else {
      var codeMatch = text.match(_stateCodePattern);
      if (codeMatch) {
        state = codeMatch[1].toUpperCase();
        text = text.replace(new RegExp("\\b" + codeMatch[1] + "\\b", "i"), " ")
          .replace(/\s{2,}/g, " ").trim().replace(/^,|,$/g, "").trim();
      }
    }

    if (!state && !zip) return String(raw).trim();

    var street = "";
    var city = "";
    if (text.indexOf(",") !== -1) {
      var parts = text.split(",").map(function (p) { return p.trim(); }).filter(Boolean);
      if (parts.length >= 2 && /\d/.test(parts[0])) {
        street = parts[0];
        city = parts[parts.length - 1];
      } else if (parts.length >= 1) {
        city = parts[parts.length - 1];
      }
    } else {
      var streetCity = text.match(new RegExp(
        "^(\\d+\\s+.{1,80}?\\b(?:street|st|avenue|ave|boulevard|blvd|road|rd|drive|dr|lane|ln|court|ct|circle|cir|way|place|pl|parkway|pkwy|highway|hwy)\\.?)\\s+(.+)$",
        "i"
      ));
      if (streetCity) {
        street = streetCity[1].trim();
        city = streetCity[2].trim();
      } else if (/^\d/.test(text)) {
        var tokens = text.split(/\s+/);
        if (tokens.length >= 3) {
          street = tokens.slice(0, -1).join(" ");
          city = tokens[tokens.length - 1];
        } else {
          city = text;
        }
      } else {
        city = text;
      }
    }

    var chunks = [];
    if (street) chunks.push(street);
    var cityState = [city, state].filter(Boolean).join(" ").trim();
    if (zip) cityState = cityState ? cityState + " " + zip : zip;
    if (cityState) chunks.push(cityState);
    return chunks.length ? chunks.join(", ") : String(raw).trim();
  }

  /** @deprecated Kept for compatibility; always returns null (non-blocking). */
  function validateAddress(addr) {
    return null;
  }

  /* ------------------------------------------------------------------------
     Time Validation / Flexible Parsing
     ------------------------------------------------------------------------ */

  /**
   * Parse a free-form time string into { hh, mm, period }.
   * Accepts: 7:00 AM, 07:00, 7am, 0700, 0800 AM, 8, etc.
   * @param {string} timeStr
   * @param {string} [defaultPeriod="AM"] used when input has no AM/PM and hour ≤ 12
   * @returns {{hh: string, mm: string, period: string}|null}
   */
  function parseFlexibleTimeString(timeStr, defaultPeriod) {
    if (!timeStr || !String(timeStr).trim()) return null;
    var stripped = String(timeStr).trim().toUpperCase().replace(/[.\u00b7]/g, ":");
    stripped = stripped.replace(/\s+/g, " ").trim();
    var periodDefault = defaultPeriod === "PM" ? "PM" : "AM";

    function finish(hour, minute, meridiem) {
      if (isNaN(hour) || isNaN(minute) || minute < 0 || minute > 59) return null;
      var period = meridiem || null;
      if (period) {
        if (hour < 1 || hour > 12) return null;
      } else if (hour >= 0 && hour <= 23) {
        // Military / 24-hour style without AM/PM
        if (hour === 0) {
          hour = 12;
          period = "AM";
        } else if (hour === 12) {
          period = "PM";
        } else if (hour > 12) {
          hour = hour - 12;
          period = "PM";
        } else {
          period = periodDefault;
        }
      } else {
        return null;
      }
      return {
        hh: String(hour).padStart(2, "0"),
        mm: String(minute).padStart(2, "0"),
        period: period,
      };
    }

    var m = stripped.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)?$/);
    if (m) return finish(parseInt(m[1], 10), parseInt(m[2], 10), m[3] || null);

    m = stripped.match(/^(\d{3,4})\s*(AM|PM)?$/);
    if (m) {
      var digits = m[1];
      var hour = digits.length === 3 ? parseInt(digits[0], 10) : parseInt(digits.slice(0, 2), 10);
      var minute = parseInt(digits.slice(-2), 10);
      return finish(hour, minute, m[2] || null);
    }

    m = stripped.match(/^(\d{1,2})\s*(AM|PM)$/);
    if (m) return finish(parseInt(m[1], 10), 0, m[2]);

    m = stripped.match(/^(\d{1,2})$/);
    if (m) return finish(parseInt(m[1], 10), 0, null);

    return null;
  }

  /**
   * Parse homepage split HH / MM fields, including compact paste into HH ("0800").
   */
  function parseFlexibleDeparture(hh, mm, period) {
    hh = (hh || "").trim();
    mm = (mm || "").trim();
    period = period === "PM" ? "PM" : "AM";

    // Compact / free-form typed into the hour field (pasted 0800, 8am, etc.)
    if (hh && !mm && !/^\d{1,2}$/.test(hh)) {
      return parseFlexibleTimeString(hh, period);
    }
    // Hour field holds a full compact time while minutes also filled — prefer hh alone
    if (/^\d{3,4}$/.test(hh)) {
      return parseFlexibleTimeString(hh + (/\b(AM|PM)\b/i.test(hh) ? "" : " " + period), period);
    }

    var raw = hh || "";
    if (mm) {
      raw = (hh || "12") + ":" + mm.padStart(2, "0");
    } else if (hh) {
      raw = hh + ":00";
    } else {
      return null;
    }
    return parseFlexibleTimeString(raw + " " + period, period);
  }

  /**
   * Validate a 12-hour time entry (HH:MM with AM/PM).
   * Returns null if valid, or an error message string if invalid.
   * Empty is allowed; missing minutes default to 00.
   */
  function validateTimeInput(hh, mm) {
    if (!hh && !mm) return null; // empty is fine — time is optional
    return parseFlexibleDeparture(hh, mm, "AM") ? null : t("error.validTime");
  }

  /**
   * Validate a time string in HH:MM format (used in modals).
   * Returns null if valid, or an error message string if invalid.
   */
  function validateTimeString(timeStr) {
    if (!timeStr) return null; // empty is fine
    return parseFlexibleTimeString(timeStr, "AM") ? null : t("error.timeFormat");
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
  Bug Reporter — pre-fills a GitHub issue on jssturm/Plan-It
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