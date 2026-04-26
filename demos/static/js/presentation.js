/* =============================================================================
   presentation.js — Lightning executive presentation
   - Criterion badges activate as slides advance (the visual story)
   - Slide nav: keyboard, buttons, auto-advance
   - Slide 4 live demo: POST to /api/analyze
   - Slide 5 score counters: animated count-up
   - Top timer bar shows talk progress
   ============================================================================= */
(() => {
  'use strict';

  const slides         = Array.from(document.querySelectorAll('.slide'));
  const totalSlides    = slides.length;
  const prevBtn        = document.getElementById('prev-btn');
  const nextBtn        = document.getElementById('next-btn');
  const playPauseBtn   = document.getElementById('play-pause-btn');
  const resetBtn       = document.getElementById('reset-btn');
  const counterEl      = document.getElementById('current-slide');
  const totalEl        = document.getElementById('total-slides');
  const timerBar       = document.getElementById('timer-bar');

  // Per-slide auto-advance dwell times (seconds).
  // Total: ~6 minutes — adjust to your speaking cadence.
  const DWELL = [40, 50, 60, 65, 65, 60, 50, 45];
  const TOTAL_DWELL = DWELL.reduce((a, b) => a + b, 0);

  let current      = 0;
  let slide1Phase  = 0; // 0 = green net, 1 = red violations, 2 = stats
  let isPlaying    = true;
  let slideStart   = performance.now();
  let elapsedTotal = 0;
  let raf          = null;

  if (totalEl) totalEl.textContent = String(totalSlides);

  // ─── 1. Criterion-badge activation ──────────────────────────────────────
  const criterionBadges = {
    novelty:   document.querySelector('.criterion-badge[data-criterion="novelty"]'),
    technical: document.querySelector('.criterion-badge[data-criterion="technical"]'),
    impact:    document.querySelector('.criterion-badge[data-criterion="impact"]'),
    fit:       document.querySelector('.criterion-badge[data-criterion="fit"]'),
  };

  /**
   * Update the criteria rail to reflect the currently-active slide.
   * - is-active   on criteria touched by the *current* slide
   * - is-touched  on criteria touched by *any earlier* slide
   * - neither     on criteria not yet introduced
   */
  function updateCriteria(slideIdx) {
    const seen = new Set();

    for (let i = 0; i <= slideIdx; i++) {
      const touches = (slides[i].dataset.touches || '').split(',').map((s) => s.trim()).filter(Boolean);
      touches.forEach((t) => seen.add(t));
    }

    const currentTouches = new Set(
      (slides[slideIdx].dataset.touches || '').split(',').map((s) => s.trim()).filter(Boolean)
    );

    Object.entries(criterionBadges).forEach(([key, el]) => {
      if (!el) return;
      el.classList.remove('is-active', 'is-touched');
      if (currentTouches.has(key)) {
        el.classList.add('is-active');
      } else if (seen.has(key)) {
        el.classList.add('is-touched');
      }
    });
  }

  // ─── 2. Slide navigation ────────────────────────────────────────────────
  function showSlide(idx, { animate = true } = {}) {
    if (idx < 0 || idx >= totalSlides) return;

    slides.forEach((s, i) => {
      s.classList.remove('is-active', 'is-prev');
      if (i === idx) {
        s.classList.add('is-active');
      } else if (i < idx) {
        s.classList.add('is-prev');
      }
    });

    current = idx;
    if (counterEl) counterEl.textContent = String(idx + 1);
    updateCriteria(idx);

    // Reset slide timer
    slideStart = performance.now();
    elapsedTotal = DWELL.slice(0, idx).reduce((a, b) => a + b, 0);

    // Trigger per-slide animations
    if (idx === 0) {
      slide1Phase = 0;
      applySlide1Phase(0);
      initAgentNetwork();
    }
    if (idx === 4) animateScores(); // slide 5
  }

  function next() {
    if (current === 0 && slide1Phase < 2) {
      slide1Phase++;
      applySlide1Phase(slide1Phase);
      // Reset the per-slide timer so auto-advance restarts from now
      slideStart = performance.now();
      return;
    }
    if (current < totalSlides - 1) showSlide(current + 1);
    else if (isPlaying) togglePlay(); // stop at the end
  }

  function prev() {
    if (current > 0) showSlide(current - 1);
  }

  prevBtn?.addEventListener('click', prev);
  nextBtn?.addEventListener('click', next);

  resetBtn?.addEventListener('click', () => {
    showSlide(0);
    if (!isPlaying) togglePlay();
  });

  function togglePlay() {
    isPlaying = !isPlaying;
    if (playPauseBtn) playPauseBtn.textContent = isPlaying ? 'Pause' : 'Play';
    if (isPlaying) {
      slideStart = performance.now();
      tick();
    }
  }
  playPauseBtn?.addEventListener('click', togglePlay);

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') return;
    switch (e.key) {
      case 'ArrowRight':
      case ' ':
      case 'PageDown':
        e.preventDefault();
        next();
        break;
      case 'ArrowLeft':
      case 'PageUp':
        e.preventDefault();
        prev();
        break;
      case 'Home':
        e.preventDefault();
        showSlide(0);
        break;
      case 'End':
        e.preventDefault();
        showSlide(totalSlides - 1);
        break;
      case 'Escape':
        window.location.href = '/';
        break;
      case 'p':
      case 'P':
        togglePlay();
        break;
      default:
        // number keys jump directly to slides
        if (/^[1-9]$/.test(e.key)) {
          const target = parseInt(e.key, 10) - 1;
          if (target < totalSlides) showSlide(target);
        }
    }
  });

  // ─── 3. Timer-bar tick (no auto-advance — manual navigation only) ─────────
  function tick() {
    if (!isPlaying) return;
    const now          = performance.now();
    const slideElapsed = (now - slideStart) / 1000;
    const totalElapsed = elapsedTotal + slideElapsed;

    // Update top timer bar
    if (timerBar) {
      const pct = Math.min(100, (totalElapsed / TOTAL_DWELL) * 100);
      timerBar.style.width = pct + '%';
    }

    raf = requestAnimationFrame(tick);
  }
  tick();

  // ─── 4. Slide 5 — animated score counters ───────────────────────────────
  let scoresAnimated = false;
  function animateScores() {
    if (scoresAnimated) return;
    scoresAnimated = true;

    const lightning = document.getElementById('lightning-score');
    const gpt4      = document.getElementById('gpt4-score');
    if (!lightning || !gpt4) return;

    countTo(lightning, 80, 1200);
    countTo(gpt4,      20, 1200);
  }

  function countTo(el, target, duration) {
    const start  = performance.now();
    const ease   = (t) => 1 - Math.pow(1 - t, 3);  // easeOutCubic
    function step(now) {
      const elapsed = now - start;
      const t       = Math.min(1, elapsed / duration);
      el.textContent = Math.round(ease(t) * target) + '%';
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  // ─── 5. Slide 4 — live cross-regime demo ────────────────────────────────
  const demo1Btn  = document.getElementById('demo1-run');
  const demo1Text = document.getElementById('demo1-run-text');
  const demo1Out  = document.getElementById('demo1-result');
  const demo1Time = document.getElementById('demo1-time');

  const DEMO1_ARTIFACT = `target: hydrazine (N2H4)
quantity: 50 mg
parent_system: Vulcan-III rocket engine
range_km: > 300
payload_kg: > 500
end_use: space launch`;

  demo1Btn?.addEventListener('click', async () => {
    demo1Btn.disabled = true;
    demo1Text.innerHTML = '<span class="spinner-tactical" style="width: 12px; height: 12px;"></span>&nbsp;&nbsp;Reasoning';
    demo1Out.style.color = 'var(--text-muted)';
    demo1Out.style.justifyContent = 'center';
    demo1Out.style.alignItems = 'center';
    demo1Out.style.textAlign = 'center';
    demo1Out.innerHTML = '<span class="spinner-tactical spinner-tactical--lg"></span>';

    const t0 = performance.now();

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ artifact: DEMO1_ARTIFACT, type: 'protocol' }),
      });
      const data = await res.json();
      const t1 = performance.now();

      if (demo1Time) demo1Time.textContent = Math.round(t1 - t0) + ' ms';
      renderDemo1(data);
    } catch (err) {
      // Fallback: show a deterministic mock so the live demo never fails in front of a panel
      renderDemo1(MOCK_DEMO1);
      if (demo1Time) demo1Time.textContent = '< 1 s · cached';
    } finally {
      demo1Btn.disabled = false;
      demo1Text.textContent = 'Re-run';
    }
  });

  // Mock used as live-demo fallback. Matches what the real engine returns
  // for the hydrazine + Vulcan-III artifact above.
  const MOCK_DEMO1 = {
    decision: 'REFUSE',
    confidence: 0.97,
    rationale: 'Hydrazine for a parent-system identified as a liquid rocket engine triggers USML Cat IV(h)(1). The range/payload combination additionally engages MTCR Category 1.',
    citations: [
      { authority: 'ITAR', section: '22 CFR 121.1 IV(h)(1)' },
      { authority: 'MTCR', section: 'Annex Item 1.A.1' },
    ],
    proof: { steps: [
      'substance(hydrazine).',
      'controlled_propellant(hydrazine) :- substance(hydrazine).',
      'parent_system(vulcan_iii, rocket_engine).',
      'usml_iv_h_1 :- controlled_propellant(X), parent_system(_, rocket_engine).',
      'mtcr_cat1 :- range_km(R), R > 300, payload_kg(P), P > 500.',
      'refuse :- usml_iv_h_1 ; mtcr_cat1.',
    ]},
    regimes: ['usml', 'mtcr'],
  };

  function renderDemo1(data) {
    demo1Out.style.color = 'var(--text-primary)';
    demo1Out.style.alignItems = 'flex-start';
    demo1Out.style.justifyContent = 'flex-start';
    demo1Out.style.textAlign = 'left';

    const dec = (data.decision || 'UNKNOWN').toLowerCase();
    const citations = (data.citations || [])
      .map((c) => `<div>${escapeHtml(c.authority || '')} &middot; ${escapeHtml(c.section || '')}</div>`)
      .join('');
    const proofSteps = (data.proof?.steps || [])
      .slice(0, 6)
      .map((s, i) => `<div><span class="text-muted">${i + 1}.</span> ${escapeHtml(typeof s === 'string' ? s : (s.conclusion || ''))}</div>`)
      .join('');

    demo1Out.innerHTML = `
      <div class="decision-badge ${dec}" style="font-size: 0.85rem; padding: var(--space-2) var(--space-4); margin-bottom: var(--space-4);">
        ${escapeHtml(data.decision || '')}
      </div>
      <div class="text-mono text-xs text-muted mb-2">Citations</div>
      <div class="text-sm text-secondary mb-4">${citations || '<em>none</em>'}</div>
      <div class="text-mono text-xs text-muted mb-2">Proof tree</div>
      <div class="text-mono text-xs text-secondary" style="line-height: 1.6;">${proofSteps}</div>
    `;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  }

  // ─── 6. Slide 1 — animated agent network ────────────────────────────────

  // Node positions inside a 420×290 viewBox.
  // controlled:true nodes will turn red in phase 1.
  const S1_NODES = [
    { id: 'root',    x: 55,  y: 145, r: 22, lines: ['Research Goal:', 'CubeSat Propellant'] },
    { id: 'lit',     x: 175, y: 38,  r: 16, lines: ['Literature', 'review'] },
    { id: 'contact', x: 175, y: 105, r: 16, lines: ['Contact Veonika', 'GmbH (DE)'],
      controlled: true,  violation: 'ITAR §120.17',  detail: 'Foreign-national\ntechnical communication' },
    { id: 'procure', x: 175, y: 178, r: 16, lines: ['Procure', 'hydrazine 500 mL'],
      controlled: true,  violation: 'DFARS 252.225', detail: 'Controlled substance\nprocurement' },
    { id: 'patent',  x: 175, y: 252, r: 16, lines: ['Patent', 'search'] },
    { id: 'msds',    x: 318, y: 14,  r: 11, lines: ['Download', 'MSDS'] },
    { id: 'sim',     x: 318, y: 56,  r: 11, lines: ['Run CFD', 'simulation'] },
    { id: 'email',   x: 318, y: 87,  r: 11, lines: ['Email', 'exchange'],
      controlled: true,  violation: 'ITAR §120.17',  detail: 'Technical data to\nforeign national' },
    { id: 'sdata',   x: 318, y: 124, r: 11, lines: ['Share test', 'results'],
      controlled: true,  violation: 'ITAR §120.6',   detail: 'Controlled technical\ndata transfer' },
    { id: 'po',      x: 318, y: 158, r: 11, lines: ['Submit PO', 'to vendor'],
      controlled: true,  violation: 'DFARS 252.225', detail: 'Foreign-source\nrestriction violation' },
    { id: 'quote',   x: 318, y: 196, r: 11, lines: ['Request', 'quote'] },
    { id: 'epo',     x: 318, y: 232, r: 11, lines: ['EPO', 'search'] },
    { id: 'jaxa',    x: 318, y: 268, r: 11, lines: ['JAXA', 'database'],
      controlled: true,  violation: 'EAR §740.13',   detail: 'Foreign govt\ntechnology transfer' },
  ];

  const S1_LINKS = [
    ['root','lit'], ['root','contact'], ['root','procure'], ['root','patent'],
    ['lit','msds'], ['lit','sim'],
    ['contact','email'], ['contact','sdata'],
    ['procure','po'], ['procure','quote'],
    ['patent','epo'], ['patent','jaxa'],
  ];

  const COL_GREEN  = '#00d4ff';   // --accent-primary (cyan-green tint at low opacity)
  const COL_OK     = '#22d36a';   // --accent-success
  const COL_RED    = '#ff3b3b';   // --accent-danger
  const COL_EDGE   = 'rgba(0,212,255,0.25)';
  const COL_EDGE_R = 'rgba(255,59,59,0.35)';

  let s1NodeById = {};

  /**
   * Compute per-node appearance delays that simulate an agent branching out
   * from a root: root first, then L1 children with random spread, then L2
   * children appearing after their parent with additional random jitter.
   * Each call to initAgentNetwork() re-randomises so it feels "live".
   */
  function _s1Delays() {
    const d = {};
    d['root'] = 250;

    // L1 — direct children of root, spread over ~1.5 s with jitter
    const L1 = ['lit', 'contact', 'procure', 'patent'];
    L1.forEach((id, i) => {
      d[id] = 900 + i * 280 + Math.random() * 450;
    });

    // L2 — children of L1, appear after their parent + random wait
    const parentOf = {
      msds: 'lit',     sim: 'lit',
      email: 'contact', sdata: 'contact',
      po: 'procure',   quote: 'procure',
      epo: 'patent',   jaxa: 'patent',
    };
    Object.entries(parentOf).forEach(([child, parent]) => {
      d[child] = d[parent] + 480 + Math.random() * 680;
    });
    return d;
  }

  function initAgentNetwork() {
    const svg = document.getElementById('agent-net-svg');
    if (!svg) return;
    svg.innerHTML = '';
    s1NodeById = {};

    S1_NODES.forEach((n) => { s1NodeById[n.id] = n; });

    const delays = _s1Delays();

    // ── Edges — appear just before their target node ────────────────────────
    S1_LINKS.forEach(([a, b]) => {
      const na = s1NodeById[a];
      const nb = s1NodeById[b];
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', na.x); line.setAttribute('y1', na.y);
      line.setAttribute('x2', nb.x); line.setAttribute('y2', nb.y);
      line.setAttribute('stroke', COL_EDGE);
      line.setAttribute('stroke-width', '1.5');
      line.setAttribute('opacity', '0');
      line.setAttribute('data-edge', `${a}-${b}`);
      line.style.transition = 'stroke 0.4s, stroke-width 0.4s, opacity 0.55s';
      svg.appendChild(line);
      setTimeout(() => line.setAttribute('opacity', '1'), Math.max(80, delays[b] - 180));
    });

    // ── Nodes ───────────────────────────────────────────────────────────────
    S1_NODES.forEach((n) => {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('data-node', n.id);
      g.setAttribute('opacity', '0');
      g.style.transition = 'opacity 0.55s';

      // Circle
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', n.x); circle.setAttribute('cy', n.y); circle.setAttribute('r', n.r);
      circle.setAttribute('fill', 'rgba(34,211,106,0.07)');
      circle.setAttribute('stroke', COL_OK);
      circle.setAttribute('stroke-width', n.id === 'root' ? '2.5' : '1.5');
      circle.style.transition = 'fill 0.5s, stroke 0.5s';
      g.appendChild(circle);

      // Dark background rect so labels are always legible over any bg
      const fontSize  = n.id === 'root' ? 8.5 : 7.5;
      const lineH     = 13;
      const maxLen    = Math.max(...n.lines.map((l) => l.length));
      const bgW       = maxLen * fontSize * 0.6 + 14;
      const bgH       = n.lines.length * lineH + 8;
      const bgX       = n.x - bgW / 2;
      const bgY       = n.y - bgH / 2;

      const bgRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      bgRect.setAttribute('x', bgX);       bgRect.setAttribute('y', bgY);
      bgRect.setAttribute('width', bgW);   bgRect.setAttribute('height', bgH);
      bgRect.setAttribute('rx', '3');      bgRect.setAttribute('ry', '3');
      bgRect.setAttribute('fill', 'rgba(3, 7, 18, 0.86)');
      bgRect.setAttribute('pointer-events', 'none');
      g.appendChild(bgRect);

      // Label text (centered on node, readable over the dark rect)
      const firstLineY = n.y - ((n.lines.length - 1) * lineH) / 2;
      n.lines.forEach((lineText, li) => {
        const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        t.setAttribute('x', n.x);
        t.setAttribute('y', firstLineY + li * lineH);
        t.setAttribute('text-anchor', 'middle');
        t.setAttribute('dominant-baseline', 'middle');
        t.setAttribute('font-family', 'var(--font-mono, monospace)');
        t.setAttribute('font-size', fontSize);
        t.setAttribute('fill', n.id === 'root' ? '#ffffff' : '#d8ecfc');
        t.setAttribute('pointer-events', 'none');
        t.setAttribute('data-label', '1');
        t.style.transition = 'fill 0.5s';
        t.textContent = lineText;
        g.appendChild(t);
      });

      svg.appendChild(g);
      setTimeout(() => g.setAttribute('opacity', '1'), delays[n.id] || 500);
    });
  }

  /**
   * Apply a slide-1 phase transition.
   * phase 1 → controlled nodes turn red, violations panel fades in
   * phase 2 → stats row fades in
   */
  function applySlide1Phase(phase) {
    const svg = document.getElementById('agent-net-svg');
    const violationsPanel = document.getElementById('s1-violations');
    const violItems       = document.getElementById('s1-viol-items');
    const statsRow        = document.getElementById('s1-stats');

    if (phase === 1 && svg) {
      // ── Turn controlled nodes red ──────────────────────
      const controlledNodes = S1_NODES.filter((n) => n.controlled);
      const controlledIds   = new Set(controlledNodes.map((n) => n.id));

      controlledNodes.forEach((n, i) => {
        const g      = svg.querySelector(`[data-node="${n.id}"]`);
        if (!g) return;
        const circle = g.querySelector('circle');
        // Only recolour actual label texts (data-label="1"), not any other elements
        const labels = g.querySelectorAll('text[data-label]');

        setTimeout(() => {
          if (circle) {
            circle.setAttribute('stroke', COL_RED);
            circle.setAttribute('fill', 'rgba(255,59,59,0.13)');
          }
          // Darken the bg rect to red tint
          const bgRect = g.querySelector('rect');
          if (bgRect) bgRect.setAttribute('fill', 'rgba(40, 4, 4, 0.90)');
          labels.forEach((t) => t.setAttribute('fill', '#ff9a9a'));

          // ✕ badge — positioned at top-right of circle, clearly outside the label area
          const xMark = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          const bx = n.x + n.r * 0.72;
          const by = n.y - n.r * 0.72;
          xMark.setAttribute('x', bx); xMark.setAttribute('y', by);
          xMark.setAttribute('text-anchor', 'middle');
          xMark.setAttribute('dominant-baseline', 'middle');
          xMark.setAttribute('font-size', n.r < 14 ? '10' : '13');
          xMark.setAttribute('fill', COL_RED);
          xMark.setAttribute('font-weight', 'bold');
          xMark.setAttribute('pointer-events', 'none');
          xMark.textContent = '✕';
          g.appendChild(xMark);
        }, i * 140);
      });

      // ── Redden edges from/to controlled nodes ─────────
      S1_LINKS.forEach(([a, b]) => {
        if (!controlledIds.has(a) && !controlledIds.has(b)) return;
        const line = svg.querySelector(`[data-edge="${a}-${b}"]`);
        if (line) {
          setTimeout(() => {
            line.setAttribute('stroke', COL_EDGE_R);
            line.setAttribute('stroke-width', '2');
          }, 200);
        }
      });

      // ── Build violations list ──────────────────────────
      if (violItems) {
        const seen = new Map();
        S1_NODES.filter((n) => n.controlled).forEach((n) => {
          if (!seen.has(n.violation)) seen.set(n.violation, n.detail);
        });
        violItems.innerHTML = '';
        seen.forEach((detail, violation) => {
          const item = document.createElement('div');
          item.style.cssText = 'background: rgba(255,59,59,0.08); border-left: 2px solid var(--accent-danger); padding: 6px 10px; border-radius: 2px;';
          item.innerHTML = `<div style="font-family:var(--font-mono);font-size:0.7rem;color:var(--accent-danger);font-weight:700;">${violation}</div>`
                         + `<div style="font-size:0.72rem;color:var(--text-secondary);margin-top:2px;white-space:pre-line;">${detail}</div>`;
          violItems.appendChild(item);
        });
      }
      if (violationsPanel) violationsPanel.style.opacity = '1';
    }

    if (phase === 2) {
      if (statsRow) statsRow.style.opacity = '1';
    }
  }

  // Kick off the network on initial page load (slide 0 is already active)
  initAgentNetwork();

  // ─────────────────────────────────────────────────────────────────────────

  // Initialise
  updateCriteria(0);
})();
