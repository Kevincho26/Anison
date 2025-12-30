(() => {
  const DELIM = " — ";

  function getPageTitle() {
    const h1 = document.querySelector(".md-content h1");
    if (h1 && h1.textContent.trim()) return h1.textContent.trim();

    // Fallback: <title> suele ser "Page - Site"
    const t = document.title || "";
    return t.split(" - ")[0].trim() || "Página";
  }

  function applyHeaderTitle() {
    const headerTitle =
      document.querySelector(".md-header__title") ||
      document.querySelector("[data-md-component='header-title']");

    if (!headerTitle) return;

    const ellipsis = headerTitle.querySelector(".md-ellipsis") || headerTitle;

    // 1) Detecta y “congela” el site name base una sola vez
    //    Si ya está guardado, lo reutiliza.
    let baseSite = ellipsis.dataset.amcSiteName;
    if (!baseSite) {
      const current = (ellipsis.textContent || "").trim();
      // si ya venía con "Site — Page — Page...", tomamos solo lo primero
      baseSite = current.split(DELIM)[0].trim() || current || "Site";
      ellipsis.dataset.amcSiteName = baseSite;
    }

    // 2) Título de página actual
    const page = getPageTitle();

    // 3) Set fijo (sin acumulación)
    ellipsis.textContent = `${baseSite}${DELIM}${page}`;
    ellipsis.title = page;
  }

  // En Material con navigation.instant, esto corre en cada “page load” interno
  function run() {
    // deja que Material pinte primero y luego sobreescribimos
    requestAnimationFrame(() => requestAnimationFrame(applyHeaderTitle));
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(run);
  } else {
    document.addEventListener("DOMContentLoaded", run);
  }
})();
