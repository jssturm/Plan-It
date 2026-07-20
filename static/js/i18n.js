/* ==========================================================================
   Plan-It — Internationalization (i18n)
   ==========================================================================
   Lightweight translation system for the Plan-It SPA.
   Supports: English (en), Spanish (es). Extend by adding more language blocks.

   Usage:
     t('key')                  → translated string for current language
     t('key', { substitutions }) → with %{key} placeholder replacement
     i18nInit()                → walks DOM and replaces [data-i18n] text
     setLanguage('es')         → switches language, re-renders UI
   ========================================================================== */

(function () {
  "use strict";

  var DEFAULT_LANG = "en";
  var STORAGE_KEY = "plan-it_lang";

  /* ------------------------------------------------------------------------
     Translation Maps
     ------------------------------------------------------------------------ */
  var translations = {
    en: {
      // App / Branding
      "app.name": "Plan-It",
      "app.version": "v0.3",
      "app.tagline": "AI-powered day itinerary builder",

      // Navigation
      "nav.home": "\uD83C\uDFE0 Home",
      "nav.plan": "Plan",
      "nav.newTrip": "\u2795 New Itinerary",
      "nav.myPlans": "\uD83D\uDCC3 My Itineraries",
      "nav.savedPlan": "Saved Plan",
      "nav.noSavedPlans": "No saved itineraries yet",

      // Health
      "health.checking": "API checking...",
      "health.online": "API online",
      "health.unreachable": "API unreachable",

      // Topbar
      "topbar.newTrip": "New Itinerary",
      "topbar.myPlans": "My Itineraries",
      "topbar.itinerary": "Itinerary",
      "topbar.clearAll": "\uD83D\uDDD1 Clear All",

      // New Trip Page
      "newTrip.title": "Plan Your Day",
      "newTrip.subtitle": "Describe your day — where you're going, what you want to do — and get a complete itinerary with route maps, schedule, and operational intelligence.",
      "newTrip.whatsYourTrip": "Where are you going?",
      "newTrip.tripPlaceholder": "e.g. Drive to Kennedy Space Center from Orlando tomorrow — stop for lunch, stay overnight at a hotel near Cocoa Beach, and drive back the next morning. Need long-term parking at KSC.",
      "newTrip.tripHint": "Include as many details as possible — venue, date, mode of travel (drive/fly), meal stops, hotel stays, long-term parking, return trip, and any special interests. The more details you provide, the better your itinerary.",
      "newTrip.departureTime": "Departure Time",
      "newTrip.departureHint": "When you plan to leave. Enter the time and select AM or PM.",
      "newTrip.startingLocation": "Starting Location (Street Address, City, State, Zip Code)",
      "newTrip.startPlaceholder": "e.g. 9801 International Dr, Orlando, Florida 32819",
      "newTrip.startHint": "Required if provided — must include street address, city, state, and zip code, separated by commas.",
      "newTrip.restaurantPrefs": "Restaurant Preferences",
      "newTrip.restaurantPlaceholder": "e.g. vegetarian, Italian, $$-$$$ range",
      "newTrip.restaurantHint": "Diet, cuisine, or price preferences for meal stops.",
      "newTrip.generate": "\uD83D\uDE80 Generate Itinerary",
      "newTrip.generating": "Generating...",

      // Plan Detail Page
      "planDetail.notFound": "Plan Not Found",
      "planDetail.notFoundText": "This plan may have been removed from your session.",
      "planDetail.delete": "\uD83D\uDDD1 Delete Plan",
      "planDetail.deleteTitle": "Delete this itinerary?",
      "planDetail.deleteConfirm": "This action cannot be undone. The plan will be removed from your session.",

      // My Plans Page
      "myPlans.title": "My Itineraries",
      "myPlans.subtitle": "Previously generated itineraries stored in this session.",
      "myPlans.emptyTitle": "No saved itineraries",
      "myPlans.emptyText": "Generate your first itinerary from the New Itinerary page and it will appear here.",

      // Stats
      "stats.departure": "Departure",
      "stats.stops": "Stops",
      "stats.highPriority": "High Priority",
      "stats.venue": "Venue",

      // Sections
      "section.itinerary": "Itinerary",
      "section.schedule": "\uD83D\uDD45 Schedule",
      "section.route": "\uD83D\uDEB9 Route",
      "section.alerts": "\u26A0 Alerts",
      "section.strategy": "\uD83D\uDCA1 Strategy Notes",
      "section.parking": "\uD83C\uDFDF Airport Parking",
      "section.flights": "\u2708 Flights",
      "section.rentalCars": "\uD83D\uDE99 Rental Cars",
      "section.rideShares": "\uD83D\uDE96 Ride Shares",
      "section.hotels": "\uD83C\uDFE8 Hotels",

      // Schedule Items
      "schedule.addStop": "\u2795 Add Stop",
      "schedule.downloadCalendar": "\uD83D\uDCC5 Download Calendar",
      "schedule.viewFull": "\uD83D\uDC41 View Full Detail",
      "schedule.planAnother": "\u2795 Plan Another Trip",
      "schedule.edit": "\u270E",
      "schedule.remove": "\uD83D\uDDD1",
      "schedule.removeTitle": "Remove this stop?",
      "schedule.removeConfirm": "This will delete the schedule item. A new plan ID will be issued.",
      "schedule.reminderNone": "\uD83D\uDD14 None",
      "schedule.reminderMin": "\uD83D\uDD14 {min} min",
      "schedule.walkToHere": "\uD83D\uDEE3 Walk to here",
      "schedule.noItems": "No schedule items.",

      // Edit/Add Modal
      "modal.editTitle": "Edit Schedule Item",
      "modal.addTitle": "Add Schedule Item",
      "modal.cancel": "Cancel",
      "modal.confirm": "Confirm",
      "modal.field.time": "Time (HH:MM AM/PM)",
      "modal.field.action": "Action",
      "modal.field.priority": "Priority (high/medium/low)",
      "modal.field.walking": "Walking Time (min)",
      "modal.field.wait": "Wait Time (min)",
      "modal.field.restaurant": "Restaurant",
      "modal.field.reminder": "Reminder Before (min)",
      "modal.field.walkingMap": "Walking Map URL",
      "modal.field.mealNote": "Meal Timing Note",
      "modal.field.backup": "Backup Plan",
      "modal.field.actionPlaceholder": "Describe the activity...",
      "modal.field.restaurantPlaceholder": "Optional",
      "modal.field.mapPlaceholder": "Optional",
      "modal.field.backupPlaceholder": "Optional",
      "modal.field.reminderOptions": ["None", "5 min", "10 min", "15 min", "20 min", "25 min", "30 min", "35 min", "40 min", "45 min", "50 min", "55 min", "60 min"],
      "modal.field.priorityOptions": ["Medium", "High", "Low"],

      // Route legs
      "route.openMaps": "\uD83D\uDEE3 Open in Google Maps \u2197",
      "route.leg": "Leg",

      // Totals
      // Crowd prediction
      "crowd.predictedCrowd": "Predicted crowd: {level}/10",
      "crowd.packed": "Packed — expect long waits",
      "crowd.busy": "Busy — plan ahead",
      "crowd.moderate": "Moderate — good day to visit",
      "crowd.light": "Light — enjoy short lines",

      // Totals
      "totals.walking": "Total Walking:",
      "totals.waiting": "Total Waiting:",
      "totals.min": "min",
      "totals.walk": "walk",
      "totals.wait": "wait",

      // Badges
      "badge.walk": "{min} min walk",
      "badge.wait": "{min} min wait",
      "badge.reminder": "{min} min",
      "badge.priority.high": "high",
      "badge.priority.medium": "medium",
      "badge.priority.low": "low",

      // Buttons
      "btn.reserveParking": "\uD83D\uDCE6 Reserve Parking",
      "btn.searchFlights": "\u2708 Search Flights",
      "btn.compareCars": "\uD83D\uDE99 Compare & Book",
      "btn.openApp": "\uD83D\uDE96 Open App",
      "btn.bookNow": "\uD83C\uDFE8 Book Now",

      // Toast Messages
      "toast.itineraryGenerated": "Itinerary generated!",
      "toast.planDeleted": "Plan deleted.",
      "toast.allPlansCleared": "All saved plans cleared.",
      "toast.scheduleUpdated": "Schedule item updated.",
      "toast.scheduleRemoved": "Schedule item removed.",
      "toast.scheduleAdded": "Schedule item added.",
      "toast.reminderSet": "Reminder set to {min} min",
      "toast.reminderRemoved": "Reminder removed",
      "toast.reminderFiredMap": "\uD83D\uDD14 Reminder for {time} — map opened in new tab",
      "toast.reminderFired": "\uD83D\uDD14 Reminder for {time} — {action}",

      // Errors
      "error.describeTrip": "Please describe your trip first.",
      "error.failedGenerate": "Failed to generate itinerary.",
      "error.failedUpdate": "Failed to update schedule item.",
      "error.timeRequired": "Time and Action are required.",
      "error.validTime": "Please enter a valid departure time (e.g. 07:00).",
      "error.hourRange": "Hour must be between 1 and 12 for AM/PM format.",
      "error.minuteRange": "Minutes must be between 0 and 59.",
      "error.hourRange12": "Hour must be between 1 and 12.",
      "error.timeFormat": "Time must be in HH:MM format (e.g. 07:00).",
      "error.missingCityState": "Address is missing city and state — use a comma between them (e.g. \"Orlando, Florida\").",
      "error.missingFullAddress": "Please enter a full address with commas: street, city, state, zip (e.g. \"9801 International Dr, Orlando, Florida 32819\").",
      "error.missingStreet": "Address is missing a street number (e.g. \"9801 International Dr, Orlando, Florida 32819\").",
      "error.missingZip": "Address is missing a 5-digit zip code (e.g. \"32819\").",
      "error.missingCityState2": "Address is missing city and state. Use commas: street, city, state, zip (e.g. \"9801 International Dr, Orlando, Florida 32819\").",
      "error.missingGeneric": "Address is missing street, city, state, or zip. Use commas: street, city, state, zip.",

      // City validation
      "city.multipleStates": "Multiple states have a \"{city}\" — please specify the state (e.g. \"{city}, FL\" or \"{city}, Florida\").",

      // Confirm modals
      "confirm.clearTitle": "Clear all saved plans?",
      "confirm.clearMessage": "This will remove every itinerary from your session. This cannot be undone.",

      // Bug Report
      "bug.fab": "\uD83D\uDC1B Report a bug",
      "bug.title": "Report a bug \u00B7 alpha",
      "bug.placeholder": "What were you doing, and what went wrong?",
      "bug.privacy": "Opens a GitHub issue you confirm \u2014 nothing is sent until you click. NEVER includes your CV, profile, application answers, or job URLs.",
      "bug.cancel": "Cancel",
      "bug.openIssue": "Open GitHub issue",
      "bug.previewLabel": "Exactly what gets attached \u2014 review before sending \u2193",
      "bug.previewTitle": "[web alpha] bug report",
      "bug.envLabel": "## Environment",
      "bug.whatHappened": "## What happened",
      "bug.filedFrom": "_Filed from the in-app bug reporter. Nothing is sent until you click._",

      // Language
      "lang.label": "\uD83C\uDF10 Language",
    },

    es: {
      // App / Branding
      "app.name": "Plan-It",
      "app.version": "v0.3",
      "app.tagline": "Planificador de itinerarios diarios con IA",

      // Navigation
      "nav.home": "\uD83C\uDFE0 Inicio",
      "nav.plan": "Planificar",
      "nav.newTrip": "\u2795 Nuevo Itinerario",
      "nav.myPlans": "\uD83D\uDCC3 Mis Itinerarios",
      "nav.savedPlan": "Plan Guardado",
      "nav.noSavedPlans": "No hay itinerarios guardados",

      // Health
      "health.checking": "Verificando API...",
      "health.online": "API conectada",
      "health.unreachable": "API inaccesible",

      // Topbar
      "topbar.newTrip": "Nuevo Itinerario",
      "topbar.myPlans": "Mis Itinerarios",
      "topbar.itinerary": "Itinerario",
      "topbar.clearAll": "\uD83D\uDDD1 Eliminar Todo",

      // New Trip Page
      "newTrip.title": "Planifica Tu Día",
      "newTrip.subtitle": "Describe tu día — adónde vas, qué quieres hacer — y obtén un itinerario completo con mapas de ruta, horario e inteligencia operativa.",
      "newTrip.whatsYourTrip": "¿Adónde vas?",
      "newTrip.tripPlaceholder": "Ej. Conducir al Centro Espacial Kennedy desde Orlando mañana — parar para almorzar, pasar la noche en un hotel cerca de Cocoa Beach y volver a la mañana siguiente. Necesito estacionamiento de larga estadía en KSC.",
      "newTrip.tripHint": "Incluye tantos detalles como sea posible — lugar, fecha, modo de viaje (coche/avión), paradas para comer, estancias en hotel, estacionamiento de larga estadía, viaje de regreso e intereses especiales. Cuantos más detalles, mejor será tu itinerario.",
      "newTrip.departureTime": "Hora de Salida",
      "newTrip.departureHint": "Cuándo planeas salir. Ingresa la hora y selecciona AM o PM.",
      "newTrip.startingLocation": "Lugar de Partida (Dirección, Ciudad, Estado, Código Postal)",
      "newTrip.startPlaceholder": "Ej. 9801 International Dr, Orlando, Florida 32819",
      "newTrip.startHint": "Obligatorio si se proporciona — debe incluir dirección, ciudad, estado y código postal, separados por comas.",
      "newTrip.restaurantPrefs": "Preferencias de Restaurante",
      "newTrip.restaurantPlaceholder": "Ej. vegetariano, italiana, rango $$-$$$",
      "newTrip.restaurantHint": "Preferencias de dieta, cocina o precio para las paradas de comida.",
      "newTrip.generate": "\uD83D\uDE80 Generar Itinerario",
      "newTrip.generating": "Generando...",

      // Plan Detail Page
      "planDetail.notFound": "Plan No Encontrado",
      "planDetail.notFoundText": "Este plan puede haber sido eliminado de tu sesión.",
      "planDetail.delete": "\uD83D\uDDD1 Eliminar Plan",
      "planDetail.deleteTitle": "¿Eliminar este itinerario?",
      "planDetail.deleteConfirm": "Esta acción no se puede deshacer. El plan se eliminará de tu sesión.",

      // My Plans Page
      "myPlans.title": "Mis Itinerarios",
      "myPlans.subtitle": "Itinerarios generados anteriormente almacenados en esta sesión.",
      "myPlans.emptyTitle": "Sin itinerarios guardados",
      "myPlans.emptyText": "Genera tu primer itinerario desde la página de Nuevo Itinerario y aparecerá aquí.",

      // Stats
      "stats.departure": "Salida",
      "stats.stops": "Paradas",
      "stats.highPriority": "Prioridad Alta",
      "stats.venue": "Lugar",

      // Sections
      "section.itinerary": "Itinerario",
      "section.schedule": "\uD83D\uDD45 Horario",
      "section.route": "\uD83D\uDEB9 Ruta",
      "section.alerts": "\u26A0 Alertas",
      "section.strategy": "\uD83D\uDCA1 Notas Estratégicas",
      "section.parking": "\uD83C\uDFDF Estacionamiento",
      "section.flights": "\u2708 Vuelos",
      "section.rentalCars": "\uD83D\uDE99 Alquiler de Coches",
      "section.rideShares": "\uD83D\uDE96 Viajes Compartidos",
      "section.hotels": "\uD83C\uDFE8 Hoteles",

      // Schedule Items
      "schedule.addStop": "\u2795 Añadir Parada",
      "schedule.downloadCalendar": "\uD83D\uDCC5 Descargar Calendario",
      "schedule.viewFull": "\uD83D\uDC41 Ver Detalle Completo",
      "schedule.planAnother": "\u2795 Planificar Otro Viaje",
      "schedule.edit": "\u270E",
      "schedule.remove": "\uD83D\uDDD1",
      "schedule.removeTitle": "¿Eliminar esta parada?",
      "schedule.removeConfirm": "Esto eliminará el elemento del horario. Se emitirá un nuevo ID de plan.",
      "schedule.reminderNone": "\uD83D\uDD14 Ninguno",
      "schedule.reminderMin": "\uD83D\uDD14 {min} min",
      "schedule.walkToHere": "\uD83D\uDEE3 Caminar hasta aquí",
      "schedule.noItems": "Sin elementos en el horario.",

      // Edit/Add Modal
      "modal.editTitle": "Editar Elemento del Horario",
      "modal.addTitle": "Añadir Elemento al Horario",
      "modal.cancel": "Cancelar",
      "modal.confirm": "Confirmar",
      "modal.field.time": "Hora (HH:MM AM/PM)",
      "modal.field.action": "Acción",
      "modal.field.priority": "Prioridad (alta/media/baja)",
      "modal.field.walking": "Tiempo de Caminata (min)",
      "modal.field.wait": "Tiempo de Espera (min)",
      "modal.field.restaurant": "Restaurante",
      "modal.field.reminder": "Recordatorio Antes (min)",
      "modal.field.walkingMap": "URL del Mapa a Pie",
      "modal.field.mealNote": "Nota de Horario de Comida",
      "modal.field.backup": "Plan Alternativo",
      "modal.field.actionPlaceholder": "Describe la actividad...",
      "modal.field.restaurantPlaceholder": "Opcional",
      "modal.field.mapPlaceholder": "Opcional",
      "modal.field.backupPlaceholder": "Opcional",
      "modal.field.reminderOptions": ["Ninguno", "5 min", "10 min", "15 min", "20 min", "25 min", "30 min", "35 min", "40 min", "45 min", "50 min", "55 min", "60 min"],
      "modal.field.priorityOptions": ["Media", "Alta", "Baja"],

      // Route legs
      "route.openMaps": "\uD83D\uDEE3 Abrir en Google Maps \u2197",
      "route.leg": "Tramo",

      // Totals
      // Crowd prediction
      "crowd.predictedCrowd": "Multitud prevista: {level}/10",
      "crowd.packed": "Lleno — espera largas colas",
      "crowd.busy": "Ocupado — planifica con antelación",
      "crowd.moderate": "Moderado — buen día para visitar",
      "crowd.light": "Ligero — disfruta de colas cortas",

      // Totals
      "totals.walking": "Caminata Total:",
      "totals.waiting": "Espera Total:",
      "totals.min": "min",
      "totals.walk": "caminata",
      "totals.wait": "espera",

      // Badges
      "badge.walk": "{min} min caminata",
      "badge.wait": "{min} min espera",
      "badge.reminder": "{min} min",
      "badge.priority.high": "alta",
      "badge.priority.medium": "media",
      "badge.priority.low": "baja",

      // Buttons
      "btn.reserveParking": "\uD83D\uDCE6 Reservar Estacionamiento",
      "btn.searchFlights": "\u2708 Buscar Vuelos",
      "btn.compareCars": "\uD83D\uDE99 Comparar y Reservar",
      "btn.openApp": "\uD83D\uDE96 Abrir App",
      "btn.bookNow": "\uD83C\uDFE8 Reservar Ahora",

      // Toast Messages
      "toast.itineraryGenerated": "¡Itinerario generado!",
      "toast.planDeleted": "Plan eliminado.",
      "toast.allPlansCleared": "Todos los planes guardados eliminados.",
      "toast.scheduleUpdated": "Elemento del horario actualizado.",
      "toast.scheduleRemoved": "Elemento del horario eliminado.",
      "toast.scheduleAdded": "Elemento del horario añadido.",
      "toast.reminderSet": "Recordatorio configurado a {min} min",
      "toast.reminderRemoved": "Recordatorio eliminado",
      "toast.reminderFiredMap": "\uD83D\uDD14 Recordatorio para {time} — mapa abierto en nueva pestaña",
      "toast.reminderFired": "\uD83D\uDD14 Recordatorio para {time} — {action}",

      // Errors
      "error.describeTrip": "Por favor describe tu viaje primero.",
      "error.failedGenerate": "Error al generar el itinerario.",
      "error.failedUpdate": "Error al actualizar el elemento del horario.",
      "error.timeRequired": "Hora y Acción son obligatorios.",
      "error.validTime": "Por favor ingresa una hora de salida válida (ej. 07:00).",
      "error.hourRange": "La hora debe estar entre 1 y 12 en formato AM/PM.",
      "error.minuteRange": "Los minutos deben estar entre 0 y 59.",
      "error.hourRange12": "La hora debe estar entre 1 y 12.",
      "error.timeFormat": "La hora debe estar en formato HH:MM (ej. 07:00).",
      "error.missingCityState": "Falta ciudad y estado — usa una coma entre ellos (ej. \"Orlando, Florida\").",
      "error.missingFullAddress": "Por favor ingresa una dirección completa con comas: calle, ciudad, estado, código postal (ej. \"9801 International Dr, Orlando, Florida 32819\").",
      "error.missingStreet": "Falta el número de calle (ej. \"9801 International Dr, Orlando, Florida 32819\").",
      "error.missingZip": "Falta el código postal de 5 dígitos (ej. \"32819\").",
      "error.missingCityState2": "Falta ciudad y estado. Usa comas: calle, ciudad, estado, código postal (ej. \"9801 International Dr, Orlando, Florida 32819\").",
      "error.missingGeneric": "Falta calle, ciudad, estado o código postal. Usa comas: calle, ciudad, estado, código postal.",

      // City validation
      "city.multipleStates": "Varios estados tienen una ciudad llamada \"{city}\" — por favor especifica el estado (ej. \"{city}, FL\" o \"{city}, Florida\").",

      // Confirm modals
      "confirm.clearTitle": "¿Eliminar todos los planes?",
      "confirm.clearMessage": "Esto eliminará todos los itinerarios de tu sesión. No se puede deshacer.",

      // Bug Report
      "bug.fab": "\uD83D\uDC1B Reportar error",
      "bug.title": "Reportar error \u00B7 alpha",
      "bug.placeholder": "¿Qué estabas haciendo y qué salió mal?",
      "bug.privacy": "Abre un issue de GitHub que tú confirmas — nada se envía hasta que haces clic. NUNCA incluye tu CV, perfil, respuestas de solicitud ni URLs de trabajos.",
      "bug.cancel": "Cancelar",
      "bug.openIssue": "Abrir issue en GitHub",
      "bug.previewLabel": "Exactamente lo que se adjunta — revisa antes de enviar \u2193",
      "bug.previewTitle": "[web alpha] reporte de error",
      "bug.envLabel": "## Entorno",
      "bug.whatHappened": "## Qué pasó",
      "bug.filedFrom": "_Enviado desde el reportador de errores de la app. Nada se envía hasta que haces clic._",

      // Language
      "lang.label": "\uD83C\uDF10 Idioma",
    }
  };

  /* ------------------------------------------------------------------------
     Current Language
     ------------------------------------------------------------------------ */
  var currentLang = (function () {
    try {
      var stored = localStorage.getItem(STORAGE_KEY);
      if (stored && translations[stored]) return stored;
    } catch (e) { /* ignore */ }

    // Detect browser language
    var navLang = (navigator.language || navigator.userLanguage || "").split("-")[0];
    if (navLang && translations[navLang]) return navLang;

    return DEFAULT_LANG;
  })();

  /* ------------------------------------------------------------------------
     Translation Function
     ------------------------------------------------------------------------ */

  /**
   * Get a translated string for the given key.
   * Supports %{key} placeholder substitution.
   *
   * @param {string} key - Translation key
   * @param {object} [subs] - Optional substitution map
   * @returns {string} Translated string, or the key itself if not found
   */
  function t(key, subs) {
    var dict = translations[currentLang] || translations[DEFAULT_LANG];
    var str = dict[key];
    if (str === undefined) {
      // Fall back to English
      var enDict = translations[DEFAULT_LANG];
      str = enDict[key];
      if (str === undefined) return key;
    }
    if (subs) {
      Object.keys(subs).forEach(function (k) {
        str = str.replace(new RegExp("%\\{" + k + "\\}", "g"), subs[k]);
      });
    }
    // Support legacy {key} format too
    if (subs) {
      Object.keys(subs).forEach(function (k) {
        str = str.replace(new RegExp("\\{" + k + "\\}", "g"), subs[k]);
      });
    }
    return str;
  }

  /* ------------------------------------------------------------------------
     DOM Initialization
     ------------------------------------------------------------------------ */

  /**
   * Walk the DOM and replace text content of elements with [data-i18n] attribute.
   * Call this on page load and after language switch.
   *
   * Supports:
   *   [data-i18n]          → element text content replaced with translation
   *   [data-i18n-placeholder] → sets the placeholder attribute
   *   [data-i18n-title]    → sets the title attribute
   *   [data-i18n-html]     → sets innerHTML (use sparingly, esc HTML in translations)
   */
  function i18nInit(root) {
    root = root || document;

    // Text content
    var textEls = root.querySelectorAll("[data-i18n]");
    for (var i = 0; i < textEls.length; i++) {
      var el = textEls[i];
      var key = el.getAttribute("data-i18n");
      if (key) el.textContent = t(key);
    }

    // Placeholder
    var placeholderEls = root.querySelectorAll("[data-i18n-placeholder]");
    for (var j = 0; j < placeholderEls.length; j++) {
      var pel = placeholderEls[j];
      var pkey = pel.getAttribute("data-i18n-placeholder");
      if (pkey) pel.setAttribute("placeholder", t(pkey));
    }

    // Title attribute
    var titleEls = root.querySelectorAll("[data-i18n-title]");
    for (var k = 0; k < titleEls.length; k++) {
      var tel = titleEls[k];
      var tkey = tel.getAttribute("data-i18n-title");
      if (tkey) tel.setAttribute("title", t(tkey));
    }

    // Inner HTML (for elements that contain icons inline)
    var htmlEls = root.querySelectorAll("[data-i18n-html]");
    for (var m = 0; m < htmlEls.length; m++) {
      var hel = htmlEls[m];
      var hkey = hel.getAttribute("data-i18n-html");
      if (hkey) hel.innerHTML = t(hkey);
    }
  }

  /* ------------------------------------------------------------------------
     Language Switching
     ------------------------------------------------------------------------ */

  /**
   * Switch the current language and re-render the UI.
   * @param {string} lang - Language code (e.g. 'en', 'es')
   * @param {function} [onAfter] - Callback to re-render dynamic content
   */
  function setLanguage(lang, onAfter) {
    if (!translations[lang]) return;
    currentLang = lang;
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) { /* ignore */ }
    i18nInit();
    if (typeof onAfter === "function") onAfter();
  }

  /**
   * Get the current language code.
   * @returns {string}
   */
  function getCurrentLanguage() {
    return currentLang;
  }

  /**
   * Get the list of available languages.
   * @returns {Array<{code: string, name: string, nativeName: string}>}
   */
  function getAvailableLanguages() {
    return [
      { code: "en", name: "English", nativeName: "English" },
      { code: "es", name: "Spanish", nativeName: "Español" },
    ];
  }

  /* ------------------------------------------------------------------------
     Public API (exposed on window)
     ------------------------------------------------------------------------ */
  window.t = t;
  window.setLanguage = setLanguage;
  window.getCurrentLanguage = getCurrentLanguage;
  window.getAvailableLanguages = getAvailableLanguages;
  window.i18nInit = i18nInit;

  // Auto-initialize on DOM ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { i18nInit(); });
  } else {
    i18nInit();
  }
})();
