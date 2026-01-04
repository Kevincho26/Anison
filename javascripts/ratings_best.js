(function () {
  function stars(r) {
    const pct = Math.max(0, Math.min(100, (Number(r) / 5) * 100));
    return `<span class="anison-stars" style="--pct:${pct}%">★★★★★</span>`;
  }

  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, (m) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[m]));
  }

  function renderList(el, data, mode) {
    const thr = data.threshold ?? 3.5;

    // ✅ leer links “Best playlists” DESDE el div del markdown
    const sp = el.getAttribute("data-best-spotify");
    const yt = el.getAttribute("data-best-youtube");
    const ytm = el.getAttribute("data-best-ytmusic");

    const rated = (data.tracks || []).filter(t => typeof t.rating === "number");
    const list = rated
      .filter(t => mode === "best" ? t.rating >= thr : true)
      .sort((a, b) => (b.rating - a.rating) || (a.title || "").localeCompare(b.title || ""));

    const s = data.stats || {};
    const left = mode === "best" ? `Best songs ≥ ★ ${thr}` : `Todas (con rating)`;
    const right = mode === "best"
      ? `(${list.length}/${s.total_tracks ?? "?"} · Avg ★ ${s.avg_rating ?? "?"})`
      : `(${list.length} con rating · Avg ★ ${s.avg_rating ?? "?"})`;

    const html = `
      <div class="anison-best-header">
        <div class="anison-best-title">${esc(left)}</div>
        <div class="anison-best-meta">${esc(right)}</div>
      </div>

      <div class="anison-best-bar">
        <div class="anison-best-platforms" aria-label="Best playlist links">
          ${sp ? `<a class="anison-icon-btn is-spotify" href="${sp}" target="_blank" rel="noopener"
                  title="Abrir Best en Spotify" aria-label="Abrir Best en Spotify"></a>` : ``}
          ${yt ? `<a class="anison-icon-btn is-youtube" href="${yt}" target="_blank" rel="noopener"
                  title="Abrir Best en YouTube" aria-label="Abrir Best en YouTube"></a>` : ``}
          ${ytm ? `<a class="anison-icon-btn is-ytmusic" href="${ytm}" target="_blank" rel="noopener"
                  title="Abrir Best en YouTube Music" aria-label="Abrir Best en YouTube Music"></a>` : ``}
        </div>

        <div class="anison-best-toggle" role="tablist" aria-label="Best songs toggle">
          <button type="button" class="anison-best-pill ${mode === "best" ? "is-active" : ""}" data-mode="best">Best</button>
          <button type="button" class="anison-best-pill ${mode === "all" ? "is-active" : ""}" data-mode="all">Todas</button>
        </div>
      </div>

      <ol class="anison-best-list">
        ${list.map(t => `
          <li>
            <a href="${t.url}" target="_blank" rel="noopener">${esc(t.title)}</a>
            <span class="anison-best-artist">— ${esc(t.artist)}</span>

            <span class="anison-best-right">
              <span class="anison-best-rating">
                ${stars(t.rating)}
                <span class="anison-best-num">${Number(t.rating).toFixed(1)}</span>
              </span>

              <span class="anison-yt-actions">
                ${t.yt_op_url ? `<a class="anison-yt-btn" href="${t.yt_op_url}" target="_blank" rel="noopener">OP</a>` : ``}
                ${t.yt_song_url ? `<a class="anison-yt-btn" href="${t.yt_song_url}" target="_blank" rel="noopener">YT</a>` : ``}
              </span>
            </span>
          </li>
        `).join("")}
      </ol>
    `;

    el.innerHTML = html;

    // bind toggle
    el.querySelectorAll(".anison-best-pill").forEach(btn => {
      btn.addEventListener("click", () => {
        const next = btn.getAttribute("data-mode");
        renderList(el, data, next);
      });
    });
  }

  async function renderBox(el) {
    const url = el.getAttribute("data-ratings");
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) throw new Error(`No pude cargar: ${url}`);
    const data = await res.json();
    renderList(el, data, "best");
  }

  function init() {
    document.querySelectorAll(".anison-best-songs[data-ratings]").forEach(el => {
      renderBox(el).catch(err => {
        el.innerHTML = `<div class="admonition warning"><p><b>Best songs</b>: ${esc(err.message)}</p></div>`;
      });
    });
  }

  document.addEventListener("DOMContentLoaded", init);
  document.addEventListener("navigation:loaded", init);
})();
