/* Origin Map — app.js
   Plain JS, no build step. Loads data/pins.json into a clustered MapLibre
   source, drives the detail panel, search, tag chips and URL hashes. */
(() => {
  "use strict";

  // ---------- Config ----------
  const DATA_URL = "data/pins.json";
  const TILE_URLS = ["a", "b", "c", "d"].map(
    (s) =>
      `https://${s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{ratio}.png`,
  );
  const TILE_ATTRIBUTION =
    '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors ' +
    '&copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener">CARTO</a>';
  const INITIAL_CENTER = [10, 20];
  const INITIAL_ZOOM = 1.6;
  const MIN_ZOOM = 1;
  const MAX_ZOOM = 12;
  const OPEN_ZOOM = 5; // zoom used when a pin is opened from a hash or the list
  const EASE_MS = 600;
  const SEARCH_DEBOUNCE_MS = 150;
  const TAG_MATCH = "any"; // 'any': pin has at least one selected tag. 'all': pin has every selected tag.
  const COLORS = { dark: "#1A0B2E", primary: "#7C3AED", light: "#FAF7F2" };

  const MOBILE = window.matchMedia("(max-width: 767.98px)");
  const REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)");

  // ---------- DOM ----------
  const $ = (id) => document.getElementById(id);
  const els = {
    form: $("search-form"),
    search: $("search"),
    count: $("count"),
    clear: $("clear"),
    chips: $("chips"),
    status: $("status"),
    list: $("pin-list-items"),
    panel: $("panel"),
    handle: $("panel-handle"),
    close: $("panel-close"),
    body: $("panel-body"),
    media: $("panel-media"),
    image: $("panel-image"),
    eyebrow: $("panel-eyebrow"),
    name: $("panel-name"),
    summary: $("panel-summary"),
    article: $("panel-article"),
    reel: $("panel-reel"),
  };

  const state = {
    features: [],
    byId: new Map(),
    query: "",
    tags: new Set(),
    openId: null,
    opener: null,
  };

  const showStatus = (msg) => {
    els.status.textContent = msg;
    els.status.hidden = !msg;
  };

  if (typeof maplibregl === "undefined") {
    showStatus(
      "The map library could not be loaded. Check your connection and reload.",
    );
    return;
  }

  // ---------- Map ----------
  const map = new maplibregl.Map({
    container: "map",
    style: {
      version: 8,
      sources: {
        carto: {
          type: "raster",
          tiles: TILE_URLS,
          tileSize: 256,
          maxzoom: 18,
          attribution: TILE_ATTRIBUTION,
        },
      },
      layers: [
        {
          id: "background",
          type: "background",
          paint: { "background-color": COLORS.dark },
        },
        { id: "carto", type: "raster", source: "carto" },
      ],
    },
    center: INITIAL_CENTER,
    zoom: INITIAL_ZOOM,
    minZoom: MIN_ZOOM,
    maxZoom: MAX_ZOOM,
    maxPitch: 0,
    dragRotate: false,
    pitchWithRotate: false,
    touchPitch: false,
  });
  map.touchZoomRotate.disableRotation();
  map.keyboard.disableRotation();
  map.addControl(
    new maplibregl.NavigationControl({ showCompass: false }),
    "top-right",
  );

  const canvas = map.getCanvas();

  function addPinLayers(data) {
    map.addSource("pins", {
      type: "geojson",
      data,
      cluster: true,
      clusterRadius: 48,
      clusterMaxZoom: 9,
    });
    map.addLayer({
      id: "clusters",
      type: "circle",
      source: "pins",
      filter: ["has", "point_count"],
      paint: {
        "circle-color": COLORS.primary,
        "circle-opacity": 0.85,
        "circle-stroke-width": 2,
        "circle-stroke-color": COLORS.light,
        "circle-radius": ["step", ["get", "point_count"], 16, 5, 22, 21, 28],
      },
    });
    map.addLayer({
      id: "pins",
      type: "circle",
      source: "pins",
      filter: ["!", ["has", "point_count"]],
      paint: {
        "circle-color": COLORS.primary,
        "circle-stroke-width": 2,
        "circle-stroke-color": COLORS.light,
        "circle-radius": 9,
      },
    });
  }

  // Cluster count labels are HTML markers so they render in JetBrains Mono
  // without needing a glyph server for a symbol layer.
  const countMarkers = new Map();

  function clearClusterLabels() {
    for (const m of countMarkers.values()) m.remove();
    countMarkers.clear();
  }

  function syncClusterLabels() {
    if (!map.getSource("pins") || !map.isSourceLoaded("pins")) return;
    const feats = map.querySourceFeatures("pins", {
      filter: ["has", "point_count"],
    });
    const seen = new Set();
    for (const f of feats) {
      const id = f.properties.cluster_id;
      if (seen.has(id)) continue;
      seen.add(id);
      const label = String(f.properties.point_count_abbreviated);
      let m = countMarkers.get(id);
      if (!m) {
        const el = document.createElement("div");
        el.className = "cluster-count";
        el.setAttribute("aria-hidden", "true");
        m = new maplibregl.Marker({ element: el })
          .setLngLat(f.geometry.coordinates)
          .addTo(map);
        countMarkers.set(id, m);
      } else {
        m.setLngLat(f.geometry.coordinates);
      }
      if (m.getElement().textContent !== label)
        m.getElement().textContent = label;
    }
    for (const [id, m] of countMarkers) {
      if (!seen.has(id)) {
        m.remove();
        countMarkers.delete(id);
      }
    }
  }

  function expandCluster(feature) {
    const source = map.getSource("pins");
    const center = feature.geometry.coordinates.slice();
    Promise.resolve(
      source.getClusterExpansionZoom(feature.properties.cluster_id),
    )
      .then((zoom) => {
        map.easeTo({
          center,
          zoom: Math.min(zoom, MAX_ZOOM),
          duration: motionMs(EASE_MS),
        });
      })
      .catch(() => {});
  }

  const motionMs = (ms) => (REDUCED_MOTION.matches ? 0 : ms);

  function easeToPin(coords, zoom) {
    const w = map.getContainer().clientWidth;
    const h = map.getContainer().clientHeight;
    // Mobile: pin sits in the top third (above the 60% sheet).
    // Desktop: pin sits centred in the left two thirds (clear of the drawer).
    const offset = MOBILE.matches ? [0, -h / 6] : [-w / 6, 0];
    const target =
      zoom == null
        ? map.getZoom()
        : Math.max(map.getZoom(), Math.min(zoom, MAX_ZOOM));
    map.easeTo({
      center: coords,
      zoom: target,
      offset,
      duration: motionMs(EASE_MS),
      essential: true,
    });
  }

  // Click handling uses a small hit box so pins are easy to tap on touch screens.
  map.on("click", (e) => {
    if (!map.getLayer("pins")) return;
    const pad = 10;
    const { x, y } = e.point;
    const feats = map.queryRenderedFeatures(
      [
        [x - pad, y - pad],
        [x + pad, y + pad],
      ],
      { layers: ["clusters", "pins"] },
    );
    if (!feats.length) {
      closePanel();
      return;
    }
    const f = feats[0];
    if (f.properties.cluster) expandCluster(f);
    else openPin(String(f.properties.id), { ease: true });
  });

  for (const layer of ["clusters", "pins"]) {
    map.on("mouseenter", layer, () => {
      canvas.style.cursor = "pointer";
    });
    map.on("mouseleave", layer, () => {
      canvas.style.cursor = "";
    });
  }

  // ---------- Filtering ----------
  const normalize = (s) =>
    String(s == null ? "" : s)
      .trim()
      .toLowerCase();
  const tagsOf = (f) =>
    Array.isArray(f.properties.tags) ? f.properties.tags.map(String) : [];

  function featureMatches(f) {
    const p = f.properties;
    if (state.tags.size) {
      const t = tagsOf(f);
      const wanted = [...state.tags];
      const ok =
        TAG_MATCH === "all"
          ? wanted.every((x) => t.includes(x))
          : wanted.some((x) => t.includes(x));
      if (!ok) return false;
    }
    if (state.query) {
      const hay = normalize(
        [p.name, p.region, p.country, ...tagsOf(f)].join(" "),
      );
      if (!hay.includes(state.query)) return false;
    }
    return true;
  }

  function applyFilter() {
    const feats = state.features.filter(featureMatches);
    const source = map.getSource("pins");
    if (source) {
      clearClusterLabels();
      source.setData({ type: "FeatureCollection", features: feats });
    }
    els.count.textContent = `${feats.length} of ${state.features.length}`;
    els.clear.disabled = !state.query && !state.tags.size;
    renderList(feats);
  }

  function buildChips() {
    const tags = [...new Set(state.features.flatMap(tagsOf))].sort((a, b) =>
      a.localeCompare(b),
    );
    els.chips.replaceChildren(
      ...tags.map((tag) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "chip";
        b.dataset.tag = tag;
        b.textContent = tag;
        b.setAttribute("aria-pressed", "false");
        b.addEventListener("click", () => {
          const on = !state.tags.has(tag);
          if (on) state.tags.add(tag);
          else state.tags.delete(tag);
          b.setAttribute("aria-pressed", String(on));
          applyFilter();
        });
        return b;
      }),
    );
    els.chips.hidden = tags.length === 0;
  }

  function resetFilters() {
    state.query = "";
    state.tags.clear();
    els.search.value = "";
    for (const chip of els.chips.querySelectorAll(".chip"))
      chip.setAttribute("aria-pressed", "false");
    applyFilter();
    els.search.focus();
  }

  let searchTimer = 0;
  els.search.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      state.query = normalize(els.search.value);
      applyFilter();
    }, SEARCH_DEBOUNCE_MS);
  });
  els.form.addEventListener("submit", (e) => {
    e.preventDefault();
    clearTimeout(searchTimer);
    state.query = normalize(els.search.value);
    applyFilter();
  });
  els.clear.addEventListener("click", resetFilters);

  // ---------- Accessible pin list ----------
  function renderList(feats) {
    els.list.replaceChildren(
      ...feats.map((f) => {
        const p = f.properties;
        const li = document.createElement("li");
        const b = document.createElement("button");
        b.type = "button";
        b.dataset.id = String(p.id);
        const small = document.createElement("small");
        small.textContent = [p.region, p.country].filter(Boolean).join(" · ");
        b.append(document.createTextNode(p.name || String(p.id)), small);
        b.addEventListener("click", () =>
          openPin(String(p.id), { opener: b, zoom: OPEN_ZOOM }),
        );
        li.append(b);
        return li;
      }),
    );
  }

  // ---------- Detail panel ----------
  const isSafeUrl = (u) => /^https?:\/\/\S+$/i.test(String(u || ""));
  const safeReelId = (id) =>
    /^[A-Za-z0-9_-]{1,64}$/.test(String(id || "")) ? String(id) : "";

  function openPin(id, opts = {}) {
    const f = state.byId.get(id);
    if (!f) return;
    const p = f.properties;

    state.openId = id;
    state.opener = opts.opener || null;

    // Image
    els.media.classList.remove("no-image");
    els.image.removeAttribute("src");
    if (isSafeUrl(p.image)) {
      els.image.alt = p.name || "";
      els.image.src = p.image;
    } else {
      els.media.classList.add("no-image");
      els.image.alt = "";
    }

    els.eyebrow.textContent = [p.region, p.country].filter(Boolean).join(" · ");
    els.name.textContent = p.name || "";
    els.summary.textContent = p.summary || "";

    // Article button, only when a URL is set
    if (isSafeUrl(p.article_url)) {
      els.article.href = p.article_url;
      els.article.hidden = false;
    } else {
      els.article.removeAttribute("href");
      els.article.hidden = true;
    }

    // Reel embed, injected only now and removed on close
    els.reel.replaceChildren();
    const reel = safeReelId(p.reel_id);
    if (reel) {
      const iframe = document.createElement("iframe");
      iframe.src = `https://www.instagram.com/reel/${reel}/embed/`;
      iframe.loading = "lazy";
      iframe.title = `Instagram reel: ${p.name || id}`;
      iframe.allow = "encrypted-media";
      iframe.setAttribute("allowfullscreen", "");
      iframe.referrerPolicy = "strict-origin-when-cross-origin";
      els.reel.append(iframe);
      els.reel.hidden = false;
    } else {
      els.reel.hidden = true;
    }

    els.body.scrollTop = 0;
    els.panel.classList.remove("is-full");
    els.panel.style.transform = "";
    els.panel.classList.add("is-open");
    els.panel.inert = false;
    els.panel.setAttribute("aria-hidden", "false");
    document.body.classList.add("panel-open");

    if (location.hash.slice(1) !== encodeURIComponent(id)) {
      history.replaceState(null, "", `#${encodeURIComponent(id)}`);
    }

    if (opts.ease !== false) easeToPin(f.geometry.coordinates, opts.zoom);
    els.panel.focus({ preventScroll: true });
  }

  function closePanel(opts = {}) {
    if (state.openId === null) return;
    state.openId = null;

    els.reel.replaceChildren();
    els.reel.hidden = true;
    els.image.removeAttribute("src");

    els.panel.classList.remove("is-open", "is-full", "dragging");
    els.panel.style.transform = "";
    els.panel.inert = true;
    els.panel.setAttribute("aria-hidden", "true");
    document.body.classList.remove("panel-open");

    if (location.hash)
      history.replaceState(null, "", location.pathname + location.search);

    const target =
      state.opener && document.contains(state.opener) ? state.opener : canvas;
    state.opener = null;
    if (opts.restoreFocus !== false) target.focus({ preventScroll: true });
  }

  // A photo that fails to load leaves the plain gradient block, not a broken-image icon.
  els.image.addEventListener("error", () => {
    if (els.image.getAttribute("src")) els.media.classList.add("no-image");
  });

  els.close.addEventListener("click", () => closePanel());

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && state.openId !== null) {
      e.preventDefault();
      closePanel();
    }
  });

  // Keep Tab inside the dialog while it is open.
  els.panel.addEventListener("keydown", (e) => {
    if (e.key !== "Tab") return;
    const focusable = [
      ...els.panel.querySelectorAll(
        'button, a[href], iframe, [tabindex]:not([tabindex="-1"])',
      ),
    ].filter((el) => !el.hidden && !el.closest("[hidden]"));
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    const active = document.activeElement;
    if (e.shiftKey && (active === first || active === els.panel)) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && active === last) {
      e.preventDefault();
      first.focus();
    }
  });

  // ---------- Mobile bottom sheet drag ----------
  const sheet = {
    active: false,
    pointerId: null,
    startY: 0,
    base: 0,
    height: 0,
    lastY: 0,
    lastT: 0,
    vel: 0,
  };
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

  els.handle.addEventListener("pointerdown", (e) => {
    if (!MOBILE.matches || state.openId === null) return;
    sheet.active = true;
    sheet.pointerId = e.pointerId;
    sheet.height = els.panel.offsetHeight;
    sheet.base = els.panel.classList.contains("is-full")
      ? 0
      : sheet.height * 0.4;
    sheet.startY = sheet.lastY = e.clientY;
    sheet.lastT = performance.now();
    sheet.vel = 0;
    els.panel.classList.add("dragging");
    try {
      els.handle.setPointerCapture(e.pointerId);
    } catch (_) {
      /* ignore */
    }
  });

  els.handle.addEventListener("pointermove", (e) => {
    if (!sheet.active || e.pointerId !== sheet.pointerId) return;
    const now = performance.now();
    const dt = Math.max(1, now - sheet.lastT);
    sheet.vel = (e.clientY - sheet.lastY) / dt; // px per ms, positive = downwards
    sheet.lastY = e.clientY;
    sheet.lastT = now;
    const y = clamp(sheet.base + (e.clientY - sheet.startY), 0, sheet.height);
    els.panel.style.transform = `translateY(${y}px)`;
  });

  function endDrag(e) {
    if (!sheet.active || e.pointerId !== sheet.pointerId) return;
    sheet.active = false;
    const y = clamp(sheet.base + (e.clientY - sheet.startY), 0, sheet.height);
    const H = sheet.height;
    // A pointer that paused before release is not a fling.
    if (performance.now() - sheet.lastT > 100) sheet.vel = 0;
    els.panel.classList.remove("dragging");
    els.panel.style.transform = "";
    if (sheet.vel > 0.5 || y > H * 0.75) {
      closePanel();
      return;
    }
    const full = sheet.vel < -0.5 || y < H * 0.2;
    els.panel.classList.toggle("is-full", full);
  }
  els.handle.addEventListener("pointerup", endDrag);
  els.handle.addEventListener("pointercancel", endDrag);

  MOBILE.addEventListener("change", () => {
    sheet.active = false;
    els.panel.classList.remove("is-full", "dragging");
    els.panel.style.transform = "";
  });

  // ---------- Hash links ----------
  function openFromHash() {
    let id = "";
    try {
      id = decodeURIComponent(location.hash.slice(1));
    } catch (_) {
      id = "";
    }
    if (id && state.byId.has(id)) {
      if (state.openId !== id) openPin(id, { zoom: OPEN_ZOOM });
    } else if (!id && state.openId !== null) {
      closePanel();
    }
  }
  window.addEventListener("hashchange", openFromHash);

  // ---------- Boot ----------
  const mapReady = new Promise((resolve) => map.once("load", resolve));
  const dataReady = fetch(DATA_URL).then((r) => {
    if (!r.ok) throw new Error(`Failed to load ${DATA_URL}: ${r.status}`);
    return r.json();
  });

  Promise.all([mapReady, dataReady])
    .then(([, data]) => {
      const feats = (Array.isArray(data.features) ? data.features : []).filter(
        (f) =>
          f &&
          f.type === "Feature" &&
          f.geometry &&
          f.geometry.type === "Point" &&
          Array.isArray(f.geometry.coordinates) &&
          f.properties &&
          f.properties.id != null,
      );
      state.features = feats;
      for (const f of feats) state.byId.set(String(f.properties.id), f);

      addPinLayers({ type: "FeatureCollection", features: feats });
      map.on("render", syncClusterLabels);
      buildChips();
      applyFilter();
      openFromHash();
    })
    .catch((err) => {
      console.error(err);
      showStatus("Could not load the pins. Please reload the page.");
    });
})();
