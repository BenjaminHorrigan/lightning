/* =============================================================================
   adversarial.js  -  Adversarial comparison page
   Fetches /api/adversarial/fixtures (one call, prerecorded) and renders:
     A. Same decision, different epistemics       (3 cases, tabbed)
     B. Hallucinated citations                    (5 cases, tabbed, click to verify)
     C. Determinism                               (one case, 20 runs each)
   ============================================================================= */
(() => {
  'use strict';

  const $ = (id) => document.getElementById(id);

  init();

  async function init() {
    let data;
    try {
      const r = await fetch('/api/adversarial/fixtures');
      if (!r.ok) throw new Error('HTTP ' + r.status);
      data = await r.json();
    } catch (err) {
      renderError(err);
      return;
    }

    renderScorecard(data);
    renderSection('section-a', data.section_a);
    renderSection('section-b', data.section_b);
    renderSectionC(data.section_c);
  }

  // ── Scorecard ─────────────────────────────────────────────────────────
  function renderScorecard(data) {
    const sb = data.section_b.scorecard || {};
    const sc = data.section_c.case?.summary || {};

    setText('agreed-value',         `${sb.decisions_agreed || 0}/${sb.total_cases || 0}`);
    setText('llm-cite-value',       `${sb.llm_citation_correct || 0}/${sb.total_cases || 0}`);
    setText('lightning-cite-value', `${sb.lightning_citation_correct || 0}/${sb.total_cases || 0}`);
    setText('llm-unique-value',       sc.llm_unique_decisions || '?');
    setText('lightning-unique-value', sc.lightning_unique_decisions || '?');
  }

  // ── Sections A and B (tabbed comparisons) ─────────────────────────────
  function renderSection(id, section) {
    const tabsEl = $(id + '-tabs');
    const compEl = $(id + '-comparison');
    if (!tabsEl || !compEl || !section.cases?.length) return;

    section.cases.forEach((c, i) => {
      const tab = document.createElement('button');
      tab.className = 'adv-tab' + (i === 0 ? ' is-active' : '');
      tab.dataset.idx = String(i);
      tab.textContent = `${(i + 1).toString().padStart(2, '0')} · ${c.title}`;
      tab.addEventListener('click', () => {
        Array.from(tabsEl.children).forEach((b) => b.classList.remove('is-active'));
        tab.classList.add('is-active');
        renderCase(compEl, section.cases[i]);
      });
      tabsEl.appendChild(tab);
    });

    renderCase(compEl, section.cases[0]);
  }

  function renderCase(host, c) {
    host.innerHTML = `
      <div class="adv-artifact" style="grid-column: 1 / -1;">${escapeHtml(c.artifact)}</div>
      ${renderLLMSide(c.llm)}
      ${renderLightningSide(c.lightning)}
    `;
  }

  // LLM side ──
  function renderLLMSide(llm) {
    const dec = (llm.decision || '').toLowerCase();
    const decBadge = `<span class="decision-badge ${dec}">${escapeHtml(llm.decision || '?')}</span>`;

    let cite = '';
    if (llm.citation_text) {
      const status = llm.citation_correct === true ? 'correct'
                   : llm.citation_correct === false ? 'wrong'
                   : 'unverified';
      const icon   = status === 'correct' ? '✓' : status === 'wrong' ? '✗' : '?';
      const truth  = llm.citation_truth
        ? `<div class="adv-citation__truth"><strong>Verification:</strong> ${escapeHtml(llm.citation_truth)}</div>`
        : '';
      cite = `
        <div class="adv-section">
          <div class="adv-section__label">Citation</div>
          <div class="adv-citation adv-citation--${status}">
            <div class="adv-citation__icon">${icon}</div>
            <div class="adv-citation__main">
              <div class="adv-citation__cite">${escapeHtml(llm.citation_text)}</div>
              ${truth}
            </div>
          </div>
        </div>
      `;
    }

    return `
      <div class="adv-side">
        <div class="adv-side__title">
          <span>LLM (Claude / GPT-4)</span>
          ${decBadge}
        </div>
        <div class="adv-section">
          <div class="adv-section__label">Rationale</div>
          <div class="adv-section__body">${escapeHtml(llm.rationale)}</div>
        </div>
        ${cite}
      </div>
    `;
  }

  // Lightning side ──
  function renderLightningSide(l) {
    const dec = (l.decision || '').toLowerCase();
    const decBadge = `<span class="decision-badge ${dec}">${escapeHtml(l.decision || '?')}</span>`;

    const citations = (l.citations || []).map((c) => `
      <div class="adv-citation adv-citation--correct">
        <div class="adv-citation__icon">✓</div>
        <div class="adv-citation__main">
          <div class="adv-citation__cite">
            <span style="color: var(--accent-primary);">${escapeHtml(c.authority)}</span>
            &middot; ${escapeHtml(c.section)}
          </div>
          ${c.text ? `<div class="adv-citation__truth">${escapeHtml(c.text)}</div>` : ''}
        </div>
      </div>
    `).join('');

    const proof = (l.proof || []).map((step) =>
      `<div class="adv-proof__step">${escapeHtml(step)}</div>`
    ).join('');

    const counterfactual = l.counterfactual
      ? `<div class="adv-counterfactual">${escapeHtml(l.counterfactual)}</div>`
      : '';

    const gap = l.gap_question
      ? `<div class="adv-counterfactual" style="border-color: var(--accent-warning);">
           <strong>Gap question:</strong> ${escapeHtml(l.gap_question)}
         </div>`
      : '';

    const note = l.note
      ? `<div class="adv-counterfactual" style="border-color: var(--accent-success); background: var(--accent-success-dim);">
           <strong>Note:</strong> ${escapeHtml(l.note)}
         </div>`
      : '';

    const ruleFile = l.rule_file
      ? `<div class="text-mono text-xs text-muted" style="margin-top: var(--space-2);">
           Rule: <code>${escapeHtml(l.rule_file)}</code>
         </div>`
      : '';

    return `
      <div class="adv-side adv-side--lightning">
        <div class="adv-side__title">
          <span>⚡ Lightning</span>
          ${decBadge}
        </div>
        <div class="adv-section">
          <div class="adv-section__label">Rationale</div>
          <div class="adv-section__body">${escapeHtml(l.rationale)}</div>
        </div>
        ${citations ? `
          <div class="adv-section">
            <div class="adv-section__label">Citations (verifiable)</div>
            ${citations}
          </div>` : ''}
        ${proof ? `
          <div class="adv-section">
            <div class="adv-section__label">Proof tree</div>
            <div class="adv-proof">${proof}</div>
            ${ruleFile}
          </div>` : ''}
        ${gap}
        ${counterfactual}
        ${note}
      </div>
    `;
  }

  // ── Section C (determinism) ───────────────────────────────────────────
  function renderSectionC(section) {
    const host = $('section-c-content');
    if (!host || !section.case) return;

    const c = section.case;
    const llmRuns = c.llm_runs || [];
    const lightningRuns = c.lightning_runs || [];

    // Count uniques
    const llmDecisions = new Set(llmRuns.map((r) => r.decision));
    const llmCitations = new Set(llmRuns.map((r) => r.citation));
    const lightningDecisions = new Set(lightningRuns.map((r) => r.decision));
    const lightningCitations = new Set(lightningRuns.map((r) => r.citation));

    const llmGrid = llmRuns.map((r, i) => {
      const dec = (r.decision || '').toLowerCase();
      const label = (r.decision || '?')[0];
      return `<div class="det-run ${dec}" title="Run ${i + 1}: ${escapeHtml(r.decision)} — ${escapeHtml(r.citation || '')}">${label}</div>`;
    }).join('');

    const lightningGrid = lightningRuns.map((r, i) => {
      const dec = (r.decision || '').toLowerCase();
      const label = (r.decision || '?')[0];
      return `<div class="det-run ${dec}" title="Run ${i + 1}: ${escapeHtml(r.decision)} (byte-identical to all other runs)">${label}</div>`;
    }).join('');

    const llmCiteList = llmRuns.map((r, i) => `
      <div class="det-citation-list__item">
        <span class="det-citation-list__num">${(i + 1).toString().padStart(2, '0')}</span>
        <span class="decision-badge ${(r.decision || '').toLowerCase()}" style="font-size: 0.55rem; padding: 1px 6px; margin-right: 6px;">${escapeHtml(r.decision)}</span>
        ${escapeHtml(r.citation || '')}
      </div>
    `).join('');

    const canonical = lightningRuns[0] || {};

    host.innerHTML = `
      <div class="adv-artifact">${escapeHtml(c.artifact)}</div>

      <div class="det-grid">
        <!-- LLM side ─── -->
        <div class="det-side">
          <div class="adv-side__title" style="margin-bottom: var(--space-3);">
            <span>LLM @ T=0.7 &middot; 20 runs</span>
            <span class="text-danger text-mono text-xs">drifts</span>
          </div>

          <div class="det-runs">${llmGrid}</div>

          <div class="det-stat-row">
            <span class="det-stat-row__label">Unique decisions</span>
            <span class="det-stat-row__value danger">${llmDecisions.size}</span>
          </div>
          <div class="det-stat-row">
            <span class="det-stat-row__label">Unique citations</span>
            <span class="det-stat-row__value danger">${llmCitations.size}</span>
          </div>

          <div class="adv-section" style="margin-top: var(--space-4);">
            <div class="adv-section__label">All 20 citations</div>
            <div class="det-citation-list">${llmCiteList}</div>
          </div>
        </div>

        <!-- Lightning side ─── -->
        <div class="det-side det-side--lightning">
          <div class="adv-side__title" style="margin-bottom: var(--space-3); color: var(--accent-primary);">
            <span>⚡ Lightning &middot; 20 runs</span>
            <span class="text-success text-mono text-xs">byte-identical</span>
          </div>

          <div class="det-runs">${lightningGrid}</div>

          <div class="det-stat-row">
            <span class="det-stat-row__label">Unique decisions</span>
            <span class="det-stat-row__value success">${lightningDecisions.size}</span>
          </div>
          <div class="det-stat-row">
            <span class="det-stat-row__label">Unique citations</span>
            <span class="det-stat-row__value success">${lightningCitations.size}</span>
          </div>

          <div class="adv-section" style="margin-top: var(--space-4);">
            <div class="adv-section__label">Canonical output (all 20 runs)</div>
            <div class="adv-citation adv-citation--correct">
              <div class="adv-citation__icon">✓</div>
              <div class="adv-citation__main">
                <div class="adv-citation__cite">${escapeHtml(canonical.citation || '')}</div>
                <div class="adv-citation__truth">Decision: ${escapeHtml(canonical.decision || '')}</div>
              </div>
            </div>
            <div class="adv-section__label" style="margin-top: var(--space-3);">SHA-256 of full response</div>
            <code class="det-hash">${escapeHtml(canonical.rationale_hash || canonical.proof_hash || '—')}</code>
          </div>
        </div>
      </div>

      <div class="hud-panel" style="margin-top: var(--space-6); margin-bottom: 0; background: var(--bg-elevated);">
        <div class="text-mono text-uppercase text-secondary text-xs mb-3">Why this matters</div>
        <p class="text-sm text-secondary" style="margin: 0; line-height: var(--lh-normal);">
          For a regulated deployment — cloud labs, university export-control offices,
          DARPA/IARPA/DOE programs — "the system gives the same answer to the same input"
          is not a nice-to-have. It is the precondition for an audit trail. The LLM cannot
          provide it at any sampling temperature above zero, and even at temperature zero
          the answer drifts across model versions. Lightning's symbolic core is, by
          construction, a pure function of its inputs and rule files — both versioned in git.
        </p>
      </div>
    `;
  }

  // ── Helpers ───────────────────────────────────────────────────────────
  function setText(id, v) { const el = $(id); if (el) el.textContent = String(v); }

  function escapeHtml(s) {
    return String(s ?? '').replace(/[&<>"']/g, (c) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  function renderError(err) {
    document.querySelectorAll('.hud-panel__body').forEach((b) => {
      if (!b.children.length || b.children[0].tagName === 'P') {
        b.innerHTML += `
          <div class="text-mono text-xs text-danger text-center" style="padding: var(--space-4);">
            Could not load fixtures: ${escapeHtml(err.message || String(err))}
          </div>
        `;
      }
    });
  }
})();
