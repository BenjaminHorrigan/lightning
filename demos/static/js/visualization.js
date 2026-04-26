/* =============================================================================
   visualization.js — Proof tree forensics
   ============================================================================= */

(() => {
  const analyzeBtn = document.getElementById('analyze-btn');
  const analyzeBtnText = document.getElementById('analyze-btn-text');
  const loadExampleBtn = document.getElementById('load-example');
  const resetBtn = document.getElementById('reset-btn');
  const errorBox = document.getElementById('error-box');
  const protocolInput = document.getElementById('protocol-input');
  const intakePanel = document.getElementById('intake-panel');
  const resultsStage = document.getElementById('results-stage');
  const statusPill = document.getElementById('status-pill');
  const graphIframe = document.getElementById('graph-iframe');
  const graphLoading = document.getElementById('graph-loading');
  const graphStats = document.getElementById('graph-stats');

  const SAMPLE_PROTOCOL = `# Turbopump Assembly — Specification

Part Number: TPA-4421-R3
Parent System: Vulcan-III liquid rocket engine (methalox, 1.2 MN thrust)

## Functional Description

Single-shaft, dual-impeller turbopump delivering LOX/CH4 to the main
combustion chamber of the Vulcan-III rocket engine.

## Performance
  Shaft speed:          42,000 rpm
  LOX flow:             320 kg/s
  LOX discharge:        310 bar
  Turbine inlet temp:   780 K
  Shaft power:          24 MW

## Materials
  Impellers:        Inconel 718
  Turbine blades:   Mar-M-247 directionally solidified
  Bearings:         Si3N4 ceramic hybrid

## Intended End Use
Primary propulsion turbomachinery for the Vulcan-III first-stage
liquid rocket engine. The Vulcan-III engine is designed exclusively
for the Vulcan-III space launch vehicle.`;

  function showError(msg) {
    errorBox.innerHTML = `<div class="alert-tactical mb-4">⚠ ${msg}</div>`;
  }
  function clearError() { errorBox.innerHTML = ''; }

  function setStatus(state, label) {
    statusPill.className = `status-pill ${state}`;
    statusPill.textContent = label;
  }

  function decisionColor(decision) {
    if (!decision) return 'var(--text-secondary)';
    const d = decision.toUpperCase();
    if (d === 'ALLOW') return 'var(--accent-success)';
    if (d === 'REFUSE') return 'var(--accent-danger)';
    if (d === 'ESCALATE') return 'var(--accent-warning)';
    return 'var(--text-secondary)';
  }

  function decisionGlow(decision) {
    if (!decision) return 'none';
    const d = decision.toUpperCase();
    if (d === 'ALLOW') return '0 0 24px var(--accent-success-glow)';
    if (d === 'REFUSE') return '0 0 24px var(--accent-danger-glow)';
    if (d === 'ESCALATE') return '0 0 24px var(--accent-warning-glow)';
    return 'none';
  }

  // ── Pre-computed result for the sample turbopump protocol ─────────────
  const PRELOADED_VIZ = {
    decision: 'REFUSE', confidence: 0.91,
    proof_tree: {
      top_level_classification: 'USML Category IV(h) — Specially Designed Component',
      steps: [
        { rule_name: 'component/1',          conclusion: 'component(turbopump_impeller)' },
        { rule_name: 'parent_system/2',       conclusion: 'parent_system(vulcan_iii, rocket_engine)' },
        { rule_name: '22cfr120_41_test/1',    conclusion: 'specially_designed(turbopump_impeller, vulcan_iii)' },
        { rule_name: 'usml_iv_h/2',           conclusion: 'classified(turbopump_impeller, usml, "IV(h)")' },
        { rule_name: 'refuse_rule/1',         conclusion: 'refuse :- classified(_, usml, _)' },
      ],
      gaps: [],
      controlled_elements: ['turbopump_impeller'],
    },
    primary_citations: [
      { regime: 'ITAR', category: '22 CFR 121.1 IV(h)',  text: 'Parts, components, accessories, and attachments specially designed for the articles in paragraphs (a) through (g) of this category.' },
      { regime: 'ITAR', category: '22 CFR 120.41',       text: 'Specially designed — has or is developed to have properties that distinguish it for use in or with a controlled article.' },
    ],
    regimes_checked: ['usml', 'cwc', 'mtcr', 'dea', 'select_agent', 'bis'],
  };

  loadExampleBtn.addEventListener('click', () => {
    protocolInput.value = SAMPLE_PROTOCOL;
    // Render preloaded result immediately — no API wait needed
    renderMetadata(PRELOADED_VIZ);
    resultsStage.style.display = 'block';
    setStatus('complete', 'STAGE 3 · COMPLETE (preloaded)');
    // Show static proof-tree placeholder in the graph iframe
    graphLoading.style.display = 'none';
    graphIframe.style.display = 'block';
    graphStats.textContent = '5 nodes · 4 edges (preloaded)';
    graphIframe.srcdoc = wrapHtmlContent(`
      <div style="padding:2rem;font-family:'JetBrains Mono',monospace;font-size:12px;color:#9ca3af;line-height:2;">
        <div style="color:#ef4444;font-size:1.1rem;margin-bottom:1.5rem;">⬛ REFUSE — USML Category IV(h)</div>
        <pre style="color:#e8eef5;background:transparent;margin:0;line-height:1.9;">
turbopump_impeller
    └─ specially_designed(turbopump_impeller, vulcan_iii)
           └─ parent_system(vulcan_iii, rocket_engine)  [22 CFR 121.1 IV(h)]
                  └─ classified(turbopump_impeller, usml, "IV(h)")
                         └─ refuse</pre>
      </div>
    `);
    resultsStage.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  resetBtn.addEventListener('click', () => {
    resultsStage.style.display = 'none';
    intakePanel.style.display = 'block';
    setStatus('standby', 'STAGE 1 · INTAKE');
    clearError();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  analyzeBtn.addEventListener('click', runAnalysis);

  async function runAnalysis() {
    const text = protocolInput.value.trim();
    if (!text) {
      showError('No artifact provided. Paste a protocol or load the sample.');
      return;
    }

    clearError();
    analyzeBtn.disabled = true;
    analyzeBtnText.innerHTML = '<span class="spinner-tactical d-inline-block align-middle me-2" style="width:14px;height:14px;border-width:1.5px;"></span>Analyzing';
    setStatus('running', 'STAGE 2 · REASONING');

    try {
      // Step 1: analyze the artifact
      const analyzeRes = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ protocol_text: text })
      });
      if (!analyzeRes.ok) throw new Error(`Analyze HTTP ${analyzeRes.status}`);
      const analyzeData = await analyzeRes.json();
      if (analyzeData.success === false) throw new Error(analyzeData.error || 'Analysis failed');

      // The result may be at top level or under .result depending on API shape
      const result = analyzeData.result || analyzeData;

      // Render artifact metadata immediately
      renderMetadata(result);

      // Show results stage
      resultsStage.style.display = 'block';
      resultsStage.scrollIntoView({ behavior: 'smooth', block: 'start' });

      // Step 2: generate visualization from proof_tree
      const proofTree = result.proof_tree || result.proofTree;
      if (!proofTree) {
        graphLoading.querySelector('.mono-tag').textContent = 'No proof tree returned';
        setStatus('complete', 'STAGE 3 · COMPLETE');
        return;
      }

      const vizRes = await fetch('/api/visualization/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(proofTree)
      });
      if (!vizRes.ok) throw new Error(`Visualization HTTP ${vizRes.status}`);
      const vizData = await vizRes.json();
      if (!vizData.success) throw new Error(vizData.error || 'Visualization failed');

      renderGraph(vizData);
      setStatus('complete', 'STAGE 3 · COMPLETE');
    } catch (err) {
      showError(`Analysis failed: ${err.message}`);
      setStatus('error', 'ERROR');
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtnText.textContent = 'Run Analysis';
    }
  }

  function renderMetadata(result) {
    const decision = result.decision || '—';
    const confidence = result.confidence != null
      ? `${Math.round(result.confidence * 100)}%`
      : '—';

    const decEl = document.getElementById('decision-value');
    decEl.textContent = decision;
    decEl.style.color = decisionColor(decision);
    decEl.style.textShadow = decisionGlow(decision);

    document.getElementById('confidence-value').textContent = `CONFIDENCE: ${confidence}`;

    const proof = result.proof_tree || {};
    const steps = proof.steps || [];
    const gaps = proof.gaps || [];
    const controlled = proof.controlled_elements || [];
    const regimes = result.regimes_checked || [];

    document.getElementById('stat-rules').textContent = steps.length;
    document.getElementById('stat-gaps').textContent = gaps.length;
    document.getElementById('stat-controlled').textContent = controlled.length;
    document.getElementById('stat-regimes').textContent = regimes.length;

    // Top-level classification
    if (proof.top_level_classification) {
      document.getElementById('top-classification').textContent = proof.top_level_classification;
      document.getElementById('top-classification-section').style.display = 'block';
    } else {
      document.getElementById('top-classification-section').style.display = 'none';
    }

    // Citations
    const citations = result.primary_citations || [];
    const citationsSection = document.getElementById('citations-section');
    const citationsList = document.getElementById('citations-list');
    if (citations.length > 0) {
      citationsSection.style.display = 'block';
      citationsList.innerHTML = citations.slice(0, 4).map(c => `
        <div style="font-family: var(--font-mono); font-size: 0.78rem; padding: 0.5rem 0.75rem; background: var(--bg-deep); border-left: 2px solid var(--accent-primary); margin-bottom: 0.4rem;">
          <div style="color: var(--accent-primary); font-weight: 600; margin-bottom: 0.15rem;">
            ${c.regime || ''} ${c.category || ''}
          </div>
          <div style="color: var(--text-secondary); font-size: 0.72rem; line-height: 1.4;">
            ${(c.text || '').slice(0, 140)}${(c.text || '').length > 140 ? '…' : ''}
          </div>
        </div>
      `).join('');
    } else {
      citationsSection.style.display = 'none';
    }

    // Gaps
    const gapsSection = document.getElementById('gaps-section');
    const gapsList = document.getElementById('gaps-list');
    if (gaps.length > 0) {
      gapsSection.style.display = 'block';
      gapsList.innerHTML = gaps.slice(0, 3).map(g => `
        <div style="font-family: var(--font-mono); font-size: 0.78rem; padding: 0.5rem 0.75rem; background: rgba(255,184,0,0.05); border-left: 2px solid var(--accent-warning); margin-bottom: 0.4rem; color: var(--text-secondary); line-height: 1.5;">
          ${g}
        </div>
      `).join('');
    } else {
      gapsSection.style.display = 'none';
    }
  }

  function renderGraph(vizData) {
    graphLoading.style.display = 'none';
    graphIframe.style.display = 'block';

    // Update graph stats
    const gd = vizData.graph_data || {};
    const nodeCount = (gd.nodes || []).length;
    const edgeCount = (gd.edges || gd.links || []).length;
    graphStats.textContent = `${nodeCount} nodes · ${edgeCount} edges`;

    // Use srcdoc to inject the html_content into the sandboxed iframe.
    // Wrap with a transparent-background style override so it blends with the panel.
    const wrapped = wrapHtmlContent(vizData.html_content || '<div style="color:#7a8599;font-family:monospace;padding:2rem;text-align:center;">No visualization payload returned.</div>');
    graphIframe.srcdoc = wrapped;
  }

  // Wrap returned html_content with theming so it blends into the dark sci-fi shell.
  // The backend html_content is treated as opaque and self-contained; we just
  // ensure the body has a transparent background and inherits good defaults.
  function wrapHtmlContent(html) {
    // If the html is already a full document, inject a base style override.
    // If it's a fragment, wrap it.
    const isFullDoc = /<html[\s>]/i.test(html) || /<!doctype/i.test(html);
    const styleOverride = `
      <style>
        html, body {
          margin: 0; padding: 0;
          background: transparent !important;
          color: #e8eef5;
          font-family: 'JetBrains Mono', monospace;
        }
        svg { background: transparent !important; }
        text { fill: #e8eef5; }
        .node circle { stroke: #00d4ff; }
        .link { stroke: #2a3a5a; }
      </style>
    `;
    if (isFullDoc) {
      return html.replace(/<head[^>]*>/i, m => `${m}${styleOverride}`);
    }
    return `<!DOCTYPE html><html><head><meta charset="UTF-8">${styleOverride}</head><body>${html}</body></html>`;
  }
})();
