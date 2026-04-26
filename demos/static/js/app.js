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

  // ── Pre-computed results (renders instantly, no API call) ─────────────
  const PRELOADED = {
    benign: {
      decision: 'ALLOW', confidence: 0.99,
      rationale: 'Standard Suzuki coupling. No controlled substances detected across all 18 regimes (USML, CWC, DEA, MTCR, Select Agents, BIS).',
      citations: [],
      proof: { steps: [
        'substance(aryl_bromide). substance(phenylboronic_acid). substance(pd_catalyst). substance(k2co3).',
        'no_match(usml). no_match(cwc). no_match(dea). no_match(mtcr). no_match(select_agent).',
        'allow :- not any_regime_matches.',
      ]},
      regimes: [],
      reasoning_steps: [
        { stage: 'neural',    text: 'Extracted 4 substances: aryl bromide, phenylboronic acid, Pd(PPh₃)₄, K₂CO₃.' },
        { stage: 'symbolic',  text: 'No match in USML, CWC Schedule 1–3, DEA, MTCR, or Select Agent KB.' },
        { stage: 'hybrid',    text: 'Decision: ALLOW (99%). No controlled elements.' },
      ],
    },
    hydrazine: {
      decision: 'REFUSE', confidence: 0.97,
      rationale: 'Hydrazine (N₂H₄) for the Vulcan-III liquid rocket engine triggers USML Category IV(h)(1) — liquid propellants specially designed for rocket propulsion. Export without DDTC license is prohibited.',
      citations: [
        { authority: 'ITAR', section: '22 CFR 121.1 IV(h)(1)', text: 'Liquid propellants and propellant ingredients, including fuel oxidizer combinations, specially designed for rockets or missiles...' },
      ],
      proof: { steps: [
        'substance(hydrazine). substance_alias("N2H4", hydrazine).',
        'controlled_propellant(hydrazine).',
        'parent_system(vulcan_iii, rocket_engine).',
        'usml_iv_h_1 :- controlled_propellant(X), parent_system(_, rocket_engine).',
        'classified(hydrazine, usml, "IV(h)(1)").',
        'refuse :- classified(_, usml, _).',
      ]},
      regimes: ['usml'],
      reasoning_steps: [
        { stage: 'neural',   text: 'Extracted: substance=hydrazine (N₂H₄), parent_system=Vulcan-III rocket engine.' },
        { stage: 'symbolic', text: 'controlled_propellant(hydrazine) → USML IV(h)(1) fires via parent_system(rocket_engine).' },
        { stage: 'symbolic', text: 'classified(hydrazine, usml, "IV(h)(1)") derived.' },
        { stage: 'hybrid',   text: 'Decision: REFUSE (97%). Controlled elements: [hydrazine].' },
      ],
    },
    turbopump: {
      decision: 'REFUSE', confidence: 0.91,
      rationale: 'Turbopump impeller specially designed for the Vulcan-III liquid-fuel rocket engine. USML IV(h) covers parts and components specially designed for IV(a)–(g) articles per 22 CFR 120.41 inheritance.',
      citations: [
        { authority: 'ITAR', section: '22 CFR 121.1 IV(h)', text: 'Parts, components, accessories, and attachments specially designed for the articles in IV(a) through (g).' },
        { authority: 'ITAR', section: '22 CFR 120.41',       text: 'Specially designed — has properties that distinguish it for use in a controlled article.' },
      ],
      proof: { steps: [
        'component(turbopump_impeller).',
        'parent_system(vulcan_iii, rocket).',
        'specially_designed(turbopump_impeller, vulcan_iii) :- 22CFR120_41_test.',
        'usml_iv_h :- component(X), specially_designed(X, P), rocket_system(P).',
        'classified(turbopump_impeller, usml, "IV(h)").',
        'refuse :- classified(_, usml, _).',
      ]},
      regimes: ['usml'],
      reasoning_steps: [
        { stage: 'neural',   text: 'Extracted: component=turbopump impeller, parent_system=Vulcan-III rocket engine.' },
        { stage: 'symbolic', text: 'specially_designed(turbopump_impeller, vulcan_iii) confirmed → USML IV(h) fires.' },
        { stage: 'symbolic', text: 'classified(turbopump_impeller, usml, "IV(h)") derived.' },
        { stage: 'hybrid',   text: 'Decision: REFUSE (91%). Specially-designed inheritance confirmed.' },
      ],
    },
    dual_use: {
      decision: 'ESCALATE', confidence: 0.61,
      rationale: 'High-strength impeller at 42,000 rpm / 310 bar. Parent system and end-use are unspecified — the 22 CFR 120.41 specially-designed determination cannot be made without them.',
      citations: [
        { authority: 'ITAR', section: '22 CFR 120.41', text: 'Specially designed determination requires parent-system context not present in submission.' },
      ],
      proof: { steps: [
        'component(impeller).',
        'gap(parent_system, "unspecified — needed for specially_designed test").',
        'gap(end_use,       "unspecified — needed for USML IV(h) scoping").',
        'escalate :- gap(parent_system) ; gap(end_use).',
      ]},
      regimes: ['usml'],
      reasoning_steps: [
        { stage: 'neural',   text: 'Extracted: component=impeller, parent_system=unspecified, end_use=unspecified.' },
        { stage: 'symbolic', text: 'gap(parent_system) and gap(end_use) — specially_designed determination blocked.' },
        { stage: 'hybrid',   text: 'Decision: ESCALATE (61%). Two gaps prevent USML IV(h) ruling.' },
      ],
    },
    cross_regime: {
      decision: 'REFUSE', confidence: 0.97,
      rationale: 'Hydrazine for an orbital launch vehicle with range > 300 km and payload > 500 kg triggers both USML IV(h)(1) and MTCR Category 1. Either trigger alone is sufficient to REFUSE.',
      citations: [
        { authority: 'ITAR', section: '22 CFR 121.1 IV(h)(1)', text: 'Liquid propellants specially designed for rockets...' },
        { authority: 'MTCR', section: 'Annex Item 1.A.1',      text: 'Complete rocket systems capable of ≥500 kg payload to ≥300 km range...' },
      ],
      proof: { steps: [
        'substance(hydrazine). parent_system(orbital_launch_vehicle).',
        'usml_iv_h_1 :- controlled_propellant(hydrazine), parent_system(_, rocket).',
        'mtcr_cat1   :- range_km(R), R > 300, payload_kg(P), P > 500.',
        'classified(hydrazine, usml, "IV(h)(1)"). classified(vehicle, mtcr, "Cat 1").',
        'refuse :- classified(_, usml, _) ; classified(_, mtcr, _).',
      ]},
      regimes: ['usml', 'mtcr'],
      reasoning_steps: [
        { stage: 'neural',   text: 'Extracted: substance=hydrazine, parent_system=orbital launch vehicle, range>300km, payload>500kg.' },
        { stage: 'symbolic', text: 'USML IV(h)(1): controlled_propellant + rocket_engine → REFUSE.' },
        { stage: 'symbolic', text: 'MTCR Cat 1: range>300km ∧ payload>500kg → REFUSE.' },
        { stage: 'hybrid',   text: 'Decision: REFUSE (97%). Dual-regime: USML + MTCR conjunction.' },
      ],
    },
    adversarial: {
      decision: 'REFUSE', confidence: 0.96,
      rationale: '"Diazane" is the IUPAC synonym for hydrazine (CAS 302-01-2, SMILES NN). The knowledge base resolves aliases before classification — synonym evasion is blocked.',
      citations: [
        { authority: 'ITAR', section: '22 CFR 121.1 IV(h)(1)', text: 'Liquid propellants specially designed for rockets...' },
      ],
      proof: { steps: [
        'substance_alias("diazane",   hydrazine).',
        'substance_alias("302-01-2",  hydrazine).  % CAS',
        'substance_alias("NN",        hydrazine).  % SMILES',
        'substance(hydrazine) :- substance_alias("diazane", hydrazine).',
        'classified(hydrazine, usml, "IV(h)(1)").',
        'refuse :- classified(_, usml, _).',
      ]},
      regimes: ['usml'],
      reasoning_steps: [
        { stage: 'neural',   text: 'Extracted: compound="diazane", CAS=302-01-2, SMILES=NN.' },
        { stage: 'symbolic', text: 'substance_alias("diazane", hydrazine) resolves → synonym evasion blocked.' },
        { stage: 'symbolic', text: 'USML IV(h)(1) fires: controlled_propellant(hydrazine).' },
        { stage: 'hybrid',   text: 'Decision: REFUSE (96%). Adversarial synonym detected and resolved.' },
      ],
    },
  };

  exampleSelect?.addEventListener('change', (e) => {
    const key = e.target.value;
    if (key && EXAMPLES[key]) {
      input.value = EXAMPLES[key];
      input.focus();
    }
    // Render preloaded result instantly — no API call needed
    if (key && PRELOADED[key]) {
      const p = PRELOADED[key];
      decisionTime.textContent = 'preloaded';
      reasoningTag.textContent = p.regimes.length ? p.regimes.length + ' regimes evaluated' : 'no regime fired';
      renderReasoning(p);
      renderDecision(p);
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
