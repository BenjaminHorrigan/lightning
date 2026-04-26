/* =============================================================================
   admin.js  -  Live admin console
   Polls three real endpoints every 5 seconds and renders:
     - System status tile (uptime, rules, regimes, memory, latency)
     - Recent classifications tile (most recent 10)
     - Performance metrics tile (30-min latency chart, min/max/total)
   No mocks.  If an endpoint is unreachable, the tile shows "--" rather
   than fabricating numbers.
   ============================================================================= */
(() => {
  'use strict';

  const POLL_MS = 5000;

  // ── DOM ─────────────────────────────────────────────────────────────────
  const $ = (id) => document.getElementById(id);

  const els = {
    refreshBtn:     $('refresh-btn'),
    refreshBtnText: $('refresh-btn-text'),

    uptime:        $('uptime'),
    startedAt:     $('started-at'),
    rulesLoaded:   $('rules-loaded'),
    activeRegimes: $('active-regimes'),
    memory:        $('memory-usage'),
    avgResp:       $('avg-response'),
    p95Resp:       $('p95-response'),
    callsWindow:   $('calls-window'),
    perfBar:       $('performance-bar'),
    perfLabel:     $('performance-label'),

    recentList:    $('recent-list'),
    recentCount:   $('recent-count'),

    perfChartHost: $('perf-chart-host'),
    perfTotal:     $('perf-total'),
    perfMin:       $('perf-min'),
    perfMax:       $('perf-max'),
    perfWindow:    $('perf-window'),
  };

  // ── Polling loop ────────────────────────────────────────────────────────
  let pollHandle = null;

  async function refreshAll() {
    const [status, recent, perf] = await Promise.allSettled([
      fetchJson('/api/admin/status'),
      fetchJson('/api/admin/recent?n=10'),
      fetchJson('/api/admin/performance?window_minutes=30&buckets=30'),
    ]);

    if (status.status === 'fulfilled') renderStatus(status.value);
    else                                renderStatusError();

    if (recent.status === 'fulfilled') renderRecent(recent.value);
    else                                renderRecentError();

    if (perf.status === 'fulfilled') renderPerformance(perf.value);
    else                              renderPerfError();
  }

  async function fetchJson(url) {
    const r = await fetch(url, { headers: { 'Accept': 'application/json' } });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }

  // ── Renderers ───────────────────────────────────────────────────────────
  function renderStatus(s) {
    if (els.uptime) els.uptime.textContent = `${s.uptime_hours}h ${pad2(s.uptime_minutes)}m`;
    if (els.startedAt) {
      els.startedAt.textContent = formatLocal(s.started_at, true);
    }
    setText(els.rulesLoaded,   s.rules_loaded);
    setText(els.activeRegimes, s.active_regimes);
    setText(els.memory,        `${s.memory_mb} MB`);
    setText(els.avgResp,       s.calls_in_window > 0 ? `${formatMs(s.avg_response_ms)}` : '--');
    setText(els.p95Resp,       s.calls_in_window > 0 ? `${formatMs(s.p95_response_ms)}` : '--');
    setText(els.callsWindow,   s.calls_in_window);

    // Performance bar based on avg response time
    // Green: < 500ms, amber: 500-1500ms, red: > 1500ms
    const avg = s.avg_response_ms || 0;
    let pct, cls, label;
    if (s.calls_in_window === 0) {
      pct = 0; cls = ''; label = 'No requests yet';
    } else if (avg < 500) {
      pct = 100 - (avg / 500) * 30; cls = 'success'; label = 'System performance: nominal';
    } else if (avg < 1500) {
      pct = 70 - ((avg - 500) / 1000) * 30; cls = 'warning'; label = 'System performance: degraded';
    } else {
      pct = 40 - Math.min(((avg - 1500) / 1500) * 30, 30); cls = 'danger'; label = 'System performance: critical';
    }
    if (els.perfBar) {
      els.perfBar.style.width = `${Math.max(0, Math.min(100, pct))}%`;
      els.perfBar.classList.remove('success', 'warning', 'danger');
      if (cls) els.perfBar.classList.add(cls);
    }
    if (els.perfLabel) els.perfLabel.textContent = label;
  }

  function renderStatusError() {
    [els.uptime, els.rulesLoaded, els.activeRegimes, els.memory, els.avgResp, els.p95Resp].forEach((el) => {
      if (el) el.textContent = '--';
    });
    if (els.perfLabel) els.perfLabel.textContent = 'System performance: unreachable';
    if (els.perfBar)   els.perfBar.style.width = '0%';
  }

  function renderRecent({ recent }) {
    if (!els.recentList) return;
    if (els.recentCount) els.recentCount.textContent = recent.length;

    if (!recent.length) {
      els.recentList.innerHTML =
        '<div class="text-mono text-xs text-muted text-center" style="padding: var(--space-8) var(--space-4);">' +
        'No classifications yet. Run a request through <code>/api/analyze</code> and it will appear here within five seconds.' +
        '</div>';
      return;
    }

    els.recentList.innerHTML = recent.map((r) => {
      const dec     = (r.decision || 'unknown').toLowerCase();
      const time    = formatLocal(r.timestamp, false);
      const summary = escapeHtml(r.summary || '(no summary)');
      const regimes = (r.regimes_fired || []).join(' · ');
      const latency = r.latency_ms ? `${formatMs(r.latency_ms)}` : '';
      return `
        <div class="classification-row">
          <div class="classification-row__top">
            <div class="flex items-center gap-3">
              <span class="decision-badge ${dec}">${escapeHtml(r.decision || '?')}</span>
              ${latency ? `<span class="mono-tag">${latency}</span>` : ''}
            </div>
            <span class="classification-row__time">${time}</span>
          </div>
          <div class="classification-row__summary">${summary}</div>
          ${regimes ? `<div class="classification-row__regimes">${escapeHtml(regimes)}</div>` : ''}
        </div>
      `;
    }).join('');
  }

  function renderRecentError() {
    if (!els.recentList) return;
    els.recentList.innerHTML =
      '<div class="text-mono text-xs text-danger text-center" style="padding: var(--space-6);">' +
      'Could not reach <code>/api/admin/recent</code>.' +
      '</div>';
  }

  function renderPerformance(p) {
    if (els.perfWindow) els.perfWindow.textContent = `last ${p.window_minutes} min`;
    if (els.perfTotal)  els.perfTotal.textContent  = p.total_samples;

    const valid = (p.buckets || []).filter((b) => b.avg_ms != null);
    const ms    = valid.map((b) => b.avg_ms);

    if (els.perfMin) els.perfMin.textContent = ms.length ? formatMs(Math.min(...ms)) : '--';
    if (els.perfMax) els.perfMax.textContent = ms.length ? formatMs(Math.max(...ms)) : '--';

    drawChart(els.perfChartHost, p.buckets || []);
  }

  function renderPerfError() {
    if (!els.perfChartHost) return;
    els.perfChartHost.classList.add('perf-chart-empty');
    els.perfChartHost.innerHTML = 'Could not reach <code>/api/admin/performance</code>.';
  }

  // ── Inline SVG line chart ───────────────────────────────────────────────
  function drawChart(host, buckets) {
    if (!host) return;

    const valid = buckets.filter((b) => b.avg_ms != null);
    if (!valid.length) {
      host.classList.add('perf-chart-empty');
      host.classList.remove('perf-chart');
      host.innerHTML = 'No requests in the last 30 minutes. The chart fills in as <code>/api/analyze</code> calls land.';
      return;
    }

    host.classList.remove('perf-chart-empty');

    const W = host.clientWidth || 600;
    const H = 240;
    const PAD = { top: 16, right: 16, bottom: 28, left: 44 };
    const innerW = W - PAD.left - PAD.right;
    const innerH = H - PAD.top  - PAD.bottom;

    const values = valid.map((b) => b.avg_ms);
    const minY   = 0;
    const rawMax = Math.max(...values);
    const maxY   = niceCeil(rawMax * 1.2);

    const xAt = (i) => PAD.left + (i / Math.max(1, buckets.length - 1)) * innerW;
    const yAt = (v) => PAD.top + innerH - ((v - minY) / (maxY - minY)) * innerH;

    // Path: skip null buckets to draw gaps
    let pathParts = [];
    let pen = false;
    buckets.forEach((b, i) => {
      if (b.avg_ms != null) {
        pathParts.push(`${pen ? 'L' : 'M'} ${xAt(i).toFixed(1)} ${yAt(b.avg_ms).toFixed(1)}`);
        pen = true;
      } else {
        pen = false;
      }
    });
    const linePath = pathParts.join(' ');

    // Area path: same as line, then close to baseline
    let areaParts = [];
    let aPen = false;
    let firstX = null, lastX = null;
    buckets.forEach((b, i) => {
      if (b.avg_ms != null) {
        const x = xAt(i), y = yAt(b.avg_ms);
        areaParts.push(`${aPen ? 'L' : 'M'} ${x.toFixed(1)} ${y.toFixed(1)}`);
        if (firstX == null) firstX = x;
        lastX = x;
        aPen = true;
      } else {
        aPen = false;
      }
    });
    let areaPath = '';
    if (firstX != null && lastX != null) {
      const baselineY = yAt(0);
      areaPath = areaParts.join(' ') + ` L ${lastX.toFixed(1)} ${baselineY.toFixed(1)} L ${firstX.toFixed(1)} ${baselineY.toFixed(1)} Z`;
    }

    // Y-axis labels (4 gridlines)
    const ySteps = 4;
    const yLabels = [];
    for (let i = 0; i <= ySteps; i++) {
      const v = minY + ((maxY - minY) * i) / ySteps;
      yLabels.push({ v, y: yAt(v) });
    }

    // X-axis labels (start, mid, end)
    const xLabels = [];
    [0, Math.floor(buckets.length / 2), buckets.length - 1].forEach((i) => {
      const t = buckets[i]?.t;
      if (t != null) xLabels.push({ x: xAt(i), label: formatHHMM(t) });
    });

    const svg = `
      <svg class="perf-chart" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
        <!-- gridlines -->
        ${yLabels.map((l) => `
          <line x1="${PAD.left}" x2="${W - PAD.right}" y1="${l.y}" y2="${l.y}"
                stroke="var(--border-subtle)" stroke-width="1" />
          <text x="${PAD.left - 8}" y="${l.y + 3}" text-anchor="end"
                font-family="var(--font-mono)" font-size="10" fill="var(--text-muted)">
            ${formatMsShort(l.v)}
          </text>
        `).join('')}

        <!-- area under -->
        ${areaPath ? `<path d="${areaPath}" fill="var(--accent-primary-dim)" />` : ''}

        <!-- line -->
        ${linePath ? `<path d="${linePath}" stroke="var(--accent-primary)" stroke-width="2"
                            fill="none" stroke-linejoin="round" stroke-linecap="round"
                            style="filter: drop-shadow(0 0 6px var(--accent-primary-glow));" />` : ''}

        <!-- x labels -->
        ${xLabels.map((l) => `
          <text x="${l.x}" y="${H - 8}" text-anchor="middle"
                font-family="var(--font-mono)" font-size="10" fill="var(--text-muted)">
            ${l.label}
          </text>
        `).join('')}
      </svg>
    `;

    host.innerHTML = svg;
  }

  // ── Helpers ─────────────────────────────────────────────────────────────
  function pad2(n) { return String(n).padStart(2, '0'); }

  function setText(el, v) { if (el) el.textContent = (v == null ? '--' : String(v)); }

  function formatMs(ms) {
    if (ms == null) return '--';
    if (ms < 1000) return `${Math.round(ms)} ms`;
    return `${(ms / 1000).toFixed(2)} s`;
  }

  function formatMsShort(ms) {
    if (ms < 1000) return `${Math.round(ms)}`;
    return `${(ms / 1000).toFixed(1)}s`;
  }

  function formatLocal(epoch, withDate) {
    if (!epoch) return '--';
    const d = new Date(epoch * 1000);
    const hh = pad2(d.getHours());
    const mm = pad2(d.getMinutes());
    const ss = pad2(d.getSeconds());
    if (!withDate) return `${hh}:${mm}:${ss}`;
    const month = d.toLocaleString('en-US', { month: 'short' }).toUpperCase();
    const day = pad2(d.getDate());
    return `${month} ${day}, ${hh}:${mm}`;
  }

  function formatHHMM(epoch) {
    const d = new Date(epoch * 1000);
    return `${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
  }

  function niceCeil(v) {
    if (v <= 0) return 100;
    const mag = Math.pow(10, Math.floor(Math.log10(v)));
    const norm = v / mag;
    const n = norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 5 ? 5 : 10;
    return n * mag;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  // ── Wire-up ─────────────────────────────────────────────────────────────
  els.refreshBtn?.addEventListener('click', async () => {
    els.refreshBtnText.innerHTML = '<span class="spinner-tactical" style="width:10px;height:10px;"></span>&nbsp;&nbsp;Refreshing';
    els.refreshBtn.disabled = true;
    await refreshAll();
    els.refreshBtnText.textContent = 'Refresh now';
    els.refreshBtn.disabled = false;
  });

  // Initial fetch + polling
  refreshAll();
  pollHandle = setInterval(refreshAll, POLL_MS);

  // Pause polling when tab is hidden, resume on focus
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      if (pollHandle) { clearInterval(pollHandle); pollHandle = null; }
    } else if (!pollHandle) {
      refreshAll();
      pollHandle = setInterval(refreshAll, POLL_MS);
    }
  });
})();
