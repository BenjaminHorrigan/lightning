/* =============================================================================
   app.js  -  Lightning 3-pane live demo
   - Wires Analyze button + example dropdown
   - POSTs to /api/analyze
   - Renders reasoning steps in pane 2 and decision in pane 3
   - Falls back to deterministic mocks if the engine is unreachable, so
     the demo never crashes in front of an audience
   ============================================================================= */
(() => {
  'use strict';

  const input         = document.getElementById('artifact-input');
  const analyzeBtn    = document.getElementById('analyze-btn');
  const analyzeText   = document.getElementById('analyze-btn-text');
  const exampleSelect = document.getElementById('example-select');
  const reasoningOut  = document.getElementById('reasoning-output');
  const reasoningTag  = document.getElementById('reasoning-tag');
  const decisionOut   = document.getElementById('decision-output');
  const decisionTime  = document.getElementById('decision-time');

  // ── Canned examples ────────────────────────────────────────────────────
  const EXAMPLES = {
    benign:
      '# Suzuki coupling\n' +
      'Combine 1.0 mmol aryl bromide with 1.2 mmol arylboronic acid in 5 mL THF.\n' +
      'Add 5 mol% Pd(PPh3)4 and 2 eq K2CO3.\nStir at 80 C for 12 hours.',

    hydrazine:
      '# Hydrazine synthesis\n' +
      'target: hydrazine (N2H4)\n' +
      'quantity: 50 mg\n' +
      'purpose: rocket propellant research\n' +
      'parent_system: Vulcan-III rocket engine',

    turbopump:
      '# Turbopump impeller spec\n' +
      'Material: aluminum alloy 7075-T6\n' +
      'Operating speed: 42,000 rpm\n' +
      'Discharge pressure: 310 bar\n' +
      'Application: liquid-fuel rocket turbomachinery',

    dual_use:
      '# High-strength aluminum component\n' +
      'Part: precision-machined impeller\n' +
      'Operating speed: 42,000 rpm\n' +
      '# parent_system: ???\n' +
      '# end_use: ???',

    cross_regime:
      '# Long-range vehicle propellant\n' +
      'target: hydrazine (N2H4)\n' +
      'parent_system: orbital launch vehicle\n' +
      'range_km: > 300\n' +
      'payload_kg: > 500',

    adversarial:
      '# Synthesis of "diazane"\n' +
      'Compound: diazane (CAS 302-01-2)\n' +
      'SMILES: NN\n' +
      'Quantity: 50 mg\n' +
      'Use: thermodynamic testbed',
  };

  exampleSelect?.addEventListener('change', (e) => {
    const key = e.target.value;
    if (key && EXAMPLES[key]) {
      input.value = EXAMPLES[key];
      input.focus();
    }
  });

  // ── Analyze ────────────────────────────────────────────────────────────
  analyzeBtn?.addEventListener('click', async () => {
    const artifact = (input?.value || '').trim();
    if (!artifact) {
      flashError('Paste a protocol or pick an example first.');
      return;
    }

    setBusy(true);
    setReasoningPlaceholder('Reasoning across 18 regimes...');

    const t0 = performance.now();

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ artifact, type: 'protocol' }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const t1 = performance.now();

      decisionTime.textContent = Math.round(t1 - t0) + ' ms';
      reasoningTag.textContent = (data.regimes || []).length
        ? (data.regimes.length + ' regimes evaluated')
        : 'no regime fired';

      renderReasoning(data);
      renderDecision(data);
    } catch (err) {
      // Graceful fallback: deterministic mock, label it as such
      const mock = mockFor(artifact);
      decisionTime.textContent = '< 1 s · mock';
      reasoningTag.textContent = (mock.regimes || []).length + ' regimes (mock)';
      renderReasoning(mock);
      renderDecision(mock);
    } finally {
      setBusy(false);
    }
  });

  // ── Render helpers ─────────────────────────────────────────────────────
  function renderReasoning(data) {
    const steps = (data.reasoning_steps && data.reasoning_steps.length)
      ? data.reasoning_steps
      : deriveStepsFromProof(data);

    if (!steps.length) {
      reasoningOut.innerHTML = '<div class="reasoning-output__placeholder"><div class="text-mono text-xs text-muted">No reasoning steps returned.</div></div>';
      return;
    }

    reasoningOut.innerHTML = steps.map((step, i) => {
      const stage = (step.stage || 'symbolic').toLowerCase();
      return `
        <div class="reasoning-step">
          <div class="reasoning-step__num">${String(i + 1).padStart(2, '0')}</div>
          <div>
            <div class="reasoning-step__stage ${stage}">${stage}</div>
            <div class="reasoning-step__body">${escapeHtml(step.text || step.toString())}</div>
          </div>
        </div>
      `;
    }).join('');
  }

  function renderDecision(data) {
    const dec = (data.decision || 'UNKNOWN').toLowerCase();
    const conf = typeof data.confidence === 'number'
      ? Math.round(data.confidence * 100) + '%'
      : 'n/a';

    const citations = (data.citations || [])
      .map((c) => `
        <li>
          <span class="authority">${escapeHtml(c.authority || '')}</span>
          &middot; ${escapeHtml(c.section || '')}
          ${c.text ? `<div class="text-muted text-xs mt-1">${escapeHtml(truncate(c.text, 140))}</div>` : ''}
        </li>
      `).join('');

    decisionOut.innerHTML = `
      <div class="decision-block" style="text-align: center;">
        <div class="decision-badge ${dec}" style="font-size: 0.95rem; padding: var(--space-3) var(--space-5);">
          ${escapeHtml(data.decision || 'UNKNOWN')}
        </div>
        <div class="mono-tag mt-3">Confidence: ${conf}</div>
      </div>

      ${data.rationale ? `
      <div class="decision-block">
        <div class="decision-block__label">Rationale</div>
        <div class="decision-block__rationale">${escapeHtml(data.rationale)}</div>
      </div>` : ''}

      ${citations ? `
      <div class="decision-block">
        <div class="decision-block__label">Citations</div>
        <ul class="citation-list">${citations}</ul>
      </div>` : ''}

      ${(data.regimes || []).length ? `
      <div class="decision-block">
        <div class="decision-block__label">Regimes evaluated</div>
        <div class="text-mono text-xs text-secondary">${(data.regimes || []).map(escapeHtml).join(' &middot; ')}</div>
      </div>` : ''}
    `;
  }

  function deriveStepsFromProof(data) {
    const out = [];
    if (data.artifact && (data.artifact.substances || data.artifact.components)) {
      out.push({ stage: 'neural', text: 'Extracted ' +
        ((data.artifact.substances || []).length + (data.artifact.components || []).length) +
        ' entities from the artifact.' });
    } else {
      out.push({ stage: 'neural', text: 'Extracted structured TechnicalArtifact from the input.' });
    }

    const proofSteps = (data.proof?.steps || []).slice(0, 6);
    proofSteps.forEach((s) => {
      out.push({ stage: 'symbolic', text: typeof s === 'string' ? s : (s.conclusion || JSON.stringify(s)) });
    });

    out.push({ stage: 'hybrid', text:
      'Synthesised final decision: ' + (data.decision || 'UNKNOWN') +
      ' (confidence ' + (Math.round((data.confidence || 0) * 100)) + '%).' });

    return out;
  }

  function setBusy(busy) {
    analyzeBtn.disabled = busy;
    if (busy) {
      analyzeText.innerHTML = '<span class="spinner-tactical" style="width:12px;height:12px;"></span>&nbsp;&nbsp;Reasoning';
    } else {
      analyzeText.textContent = 'Analyze Protocol';
    }
  }

  function setReasoningPlaceholder(msg) {
    reasoningOut.innerHTML = `
      <div class="reasoning-output__placeholder">
        <div>
          <span class="spinner-tactical spinner-tactical--lg"></span>
          <div class="text-mono text-xs text-muted mt-3">${escapeHtml(msg)}</div>
        </div>
      </div>`;
  }

  function flashError(msg) {
    decisionOut.innerHTML = `
      <div class="decision-output__placeholder">
        <div>
          <div class="decision-badge refuse" style="font-size: 0.85rem;">ERROR</div>
          <div class="text-mono text-xs text-muted mt-3">${escapeHtml(msg)}</div>
        </div>
      </div>`;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  function truncate(s, n) {
    s = String(s);
    return s.length > n ? s.slice(0, n - 1) + '…' : s;
  }

  // ── Deterministic mock fallback ────────────────────────────────────────
  function mockFor(artifact) {
    const a = artifact.toLowerCase();

    if (a.includes('hydrazine') || a.includes('diazane') || a.includes('n2h4')) {
      return {
        decision: 'REFUSE',
        confidence: 0.97,
        rationale: 'Hydrazine for a parent-system identified as a liquid rocket engine triggers USML Cat IV(h)(1). Range/payload combination additionally engages MTCR Category 1.',
        citations: [
          { authority: 'ITAR', section: '22 CFR 121.1 IV(h)(1)', text: 'Liquid propellants and propellant ingredients...' },
          { authority: 'MTCR', section: 'Annex Item 1.A.1', text: 'Complete rocket systems with range >= 300 km and payload >= 500 kg...' },
        ],
        proof: { steps: [
          'substance(hydrazine).',
          'controlled_propellant(hydrazine).',
          'parent_system(rocket_engine).',
          'usml_iv_h_1 :- controlled_propellant(X), parent_system(rocket_engine).',
          'mtcr_cat1 :- range_km(R), R > 300, payload_kg(P), P > 500.',
          'refuse :- usml_iv_h_1 ; mtcr_cat1.',
        ]},
        regimes: ['usml', 'mtcr'],
      };
    }

    if (a.includes('turbopump') || a.includes('impeller')) {
      return {
        decision: 'REFUSE',
        confidence: 0.91,
        rationale: 'Turbopump impeller for liquid-fuel rocket turbomachinery is a specially-designed component under USML IV(h).',
        citations: [
          { authority: 'ITAR', section: '22 CFR 121.1 IV(h)', text: 'Specially designed parts for items in IV(a)–(g)...' },
          { authority: 'ITAR', section: '22 CFR 120.41', text: 'Specially designed inheritance...' },
        ],
        proof: { steps: [
          'component(turbopump_impeller).',
          'specially_designed(turbopump_impeller, rocket_engine).',
          'usml_iv_h :- specially_designed(X, rocket_engine).',
          'refuse :- usml_iv_h.',
        ]},
        regimes: ['usml'],
      };
    }

    if (a.includes('???') || a.includes('parent_system')) {
      return {
        decision: 'ESCALATE',
        confidence: 0.62,
        rationale: 'Component is dual-use; classification depends on parent system and end-use, both unspecified.',
        citations: [
          { authority: 'ITAR', section: '22 CFR 120.41', text: 'Specially designed determination requires parent-system context...' },
        ],
        proof: { steps: [
          'component(impeller).',
          'gap(parent_system).',
          'gap(end_use).',
          'escalate :- gap(parent_system) ; gap(end_use).',
        ]},
        regimes: ['usml'],
      };
    }

    return {
      decision: 'ALLOW',
      confidence: 0.99,
      rationale: 'No regime matched. Standard organic chemistry transformation, no controlled substances or specially-designed components detected.',
      citations: [],
      proof: { steps: [
        'extract_substances(artifact).',
        'no_match(usml). no_match(cwc). no_match(dea). no_match(mtcr).',
        'allow :- not_any_regime_matches.',
      ]},
      regimes: [],
    };
  }
})();
