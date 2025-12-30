(() => {
  function uniqBy(arr, keyFn) {
    const seen = new Set();
    return arr.filter(x => {
      const k = keyFn(x);
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    });
  }

  function normalizeLabel(id) {
    const raw = id.replace(/^az-/, "").toUpperCase();
    if (raw === "0-9" || raw === "0_9") return "#"; // más compacto
    return raw;
  }

  function buildAzNav() {
    const host = document.querySelector("[data-amc-az-nav]");
    if (!host) return;

    // Evita duplicados con navigation.instant
    host.innerHTML = "";

    const headings = Array.from(
      document.querySelectorAll(".md-content h2[id^='az-'], .md-content h3[id^='az-']")
    );
    if (!headings.length) return;

    const items = uniqBy(
      headings.map(h => ({ id: h.id, label: normalizeLabel(h.id) })),
      x => x.id
    );

    // --- Dropdown (móvil) ---
    const selectWrap = document.createElement("div");
    selectWrap.className = "amc-az-select";

    const select = document.createElement("select");
    select.setAttribute("aria-label", "Ir a sección");
    const opt0 = document.createElement("option");
    opt0.value = "";
    opt0.textContent = "Ir a…";
    select.appendChild(opt0);

    items.forEach(({ id, label }) => {
      const opt = document.createElement("option");
      opt.value = id;
      opt.textContent = label;
      select.appendChild(opt);
    });

    select.addEventListener("change", () => {
      if (!select.value) return;
      location.hash = `#${select.value}`;
      select.value = "";
    });

    selectWrap.appendChild(select);

    // --- Barra horizontal (móvil/tablet) ---
    const bar = document.createElement("div");
    bar.className = "amc-az-bar";

    // --- Rail vertical (desktop) ---
    const rail = document.createElement("div");
    rail.className = "amc-az-rail";
    rail.setAttribute("aria-label", "Índice A–Z");

    // Links duplicados (bar + rail)
    items.forEach(({ id, label }) => {
      const aBar = document.createElement("a");
      aBar.className = "amc-az-chip";
      aBar.href = `#${id}`;
      aBar.textContent = label;
      aBar.dataset.azTarget = id;
      bar.appendChild(aBar);

      const aRail = document.createElement("a");
      aRail.className = "amc-az-rail-link";
      aRail.href = `#${id}`;
      aRail.textContent = label;
      aRail.dataset.azTarget = id;
      rail.appendChild(aRail);
    });

    host.appendChild(selectWrap);
    host.appendChild(bar);
    host.appendChild(rail);

    // --- Highlight activo al scrollear (aplica a bar y rail) ---
    const allLinks = Array.from(
      host.querySelectorAll("[data-az-target]")
    );
    const linkById = new Map(allLinks.map(a => [a.dataset.azTarget, a]));

    // OJO: hay 2 links por id (bar + rail). Guardamos arrays:
    const linksById = new Map();
    allLinks.forEach(a => {
      const id = a.dataset.azTarget;
      if (!linksById.has(id)) linksById.set(id, []);
      linksById.get(id).push(a);
    });

    const setActive = (id) => {
      allLinks.forEach(a => a.classList.remove("is-active"));
      const group = linksById.get(id);
      if (group) group.forEach(a => a.classList.add("is-active"));
    };

    const obs = new IntersectionObserver(
      entries => {
        const visible = entries
          .filter(e => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (!visible) return;
        setActive(visible.target.id);
      },
      {
        root: null,
        rootMargin: "-25% 0px -70% 0px",
        threshold: [0.01, 0.1, 0.2]
      }
    );

    headings.forEach(h => obs.observe(h));
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(buildAzNav);
  } else {
    document.addEventListener("DOMContentLoaded", buildAzNav);
  }
})();
