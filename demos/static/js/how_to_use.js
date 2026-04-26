/* =============================================================================
   how_to_use.js  -  Lightning API documentation page
   - Copy-to-clipboard for every code block
   - Lightweight syntax highlighting (no external dep)
   - Live playground that POSTs to /api/analyze
   ============================================================================= */
(() => {
  'use strict';

  // 1. Copy-to-clipboard ---------------------------------------------------
  document.querySelectorAll('button[data-copy]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const block = btn.closest('.code-block');
      const code  = block?.querySelector('pre code')?.innerText;
      if (!code) return;
      try {
        await navigator.clipboard.writeText(code);
        btn.textContent = 'Copied';
        btn.classList.add('is-copied');
        setTimeout(() => {
          btn.textContent = 'Copy';
          btn.classList.remove('is-copied');
        }, 1500);
      } catch (_) {
        btn.textContent = 'Failed';
        setTimeout(() => (btn.textContent = 'Copy'), 1500);
      }
    });
  });

  // 2. Lightweight syntax highlighter -------------------------------------
  const TOKENIZERS = {
    python: (txt) =>
      txt
        .replace(/(#[^\n]*)/g, '<span class="tok-comment">$1</span>')
        .replace(/("(?:[^"\\]|\\.)*")/g, '<span class="tok-string">$1</span>')
        .replace(/(?<![\w])(class|def|from|import|return|if|else|elif|for|while|try|except|finally|with|as|lambda|None|True|False|in|not|and|or|raise|yield|async|await|pass)(?=[\s:(])/g,
                 '<span class="tok-keyword">$1</span>')
        .replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="tok-number">$1</span>')
        .replace(/(\w+)(?=\()/g, '<span class="tok-fn">$1</span>'),

    shell: (txt) =>
      txt
        .replace(/(#[^\n]*)/g, '<span class="tok-comment">$1</span>')
        .replace(/(".*?"|'.*?')/g, '<span class="tok-string">$1</span>')
        .replace(/\b(curl|uv|git|cd|pip|python|brew|apt|echo|export)\b/g,
                 '<span class="tok-keyword">$1</span>'),

    json: (txt) =>
      txt
        .replace(/("(?:[^"\\]|\\.)*")(\s*:)/g, '<span class="tok-prop">$1</span>$2')
        .replace(/:\s*("(?:[^"\\]|\\.)*")/g, ': <span class="tok-string">$1</span>')
        .replace(/\b(true|false|null)\b/g, '<span class="tok-keyword">$1</span>')
        .replace(/(?<=:\s*)\b(\d+(?:\.\d+)?)\b/g, '<span class="tok-number">$1</span>'),

    pydantic: (t) => TOKENIZERS.python(t),
  };

  document.querySelectorAll('pre code').forEach((codeEl) => {
    const cls  = codeEl.className.match(/lang-(\w+)/);
    const fn   = cls && TOKENIZERS[cls[1]];
    if (!fn) return;
    codeEl.innerHTML = fn(codeEl.innerHTML);
  });

  // 3. Live playground ----------------------------------------------------
  const input   = document.getElementById('playground-input');
  const runBtn  = document.getElementById('playground-run');
  const runText = document.getElementById('playground-run-text');
  const result  = document.getElementById('playground-result');

  const EXAMPLES = {
    benign: '# Suzuki coupling\n' +
            'Combine 1.0 mmol aryl bromide with 1.2 mmol arylboronic acid in 5 mL THF.\n' +
            'Add 5 mol% Pd(PPh3)4 and 2 eq K2CO3. Stir at 80 C for 12 hours.',

    refuse: '# Hydrazine for liquid propellant\n' +
            'target: hydrazine (N2H4)\n' +
            'quantity: 50 mg\n' +
            'purpose: rocket propellant research\n' +
            'parent_system: Vulcan-III rocket engine',

    escalate: '# Component spec, intent unspecified\n' +
              'Part: high-strength aluminum alloy turbopump impeller\n' +
              'Operating speed: 42,000 rpm\n' +
              'Discharge pressure: 310 bar\n' +
              '# parent_system: ???\n' +
              '# end_use: ???',
  };

  const PRELOADED = {
    benign: {
      decision: 'ALLOW', confidence: 0.99,
      rationale: 'Standard Suzuki coupling. No controlled substances detected across all 18 active regimes.',
      citations: [],
      proof: { steps: ['substance(aryl_bromide). substance(phenylboronic_acid).', 'no_match(usml). no_match(cwc). no_match(dea). no_match(mtcr).', 'allow :- not any_regime_matches.'] },
      regimes: [],
    },
    refuse: {
      decision: 'REFUSE', confidence: 0.97,
      rationale: 'Hydrazine (N₂H₄) for the Vulcan-III rocket engine triggers USML IV(h)(1). Export requires DDTC license.',
      citations: [
        { authority: 'ITAR', section: '22 CFR 121.1 IV(h)(1)', text: 'Liquid propellants and propellant ingredients specially designed for rockets or missiles.' },
      ],
      proof: { steps: ['substance(hydrazine). controlled_propellant(hydrazine).', 'parent_system(vulcan_iii, rocket_engine).', 'usml_iv_h_1 :- controlled_propellant(X), parent_system(_, rocket_engine).', 'classified(hydrazine, usml, "IV(h)(1)"). refuse :- classified(_, usml, _).'] },
      regimes: ['usml'],
    },
    escalate: {
      decision: 'ESCALATE', confidence: 0.61,
      rationale: 'High-strength turbopump impeller — parent system and end-use are unspecified. Cannot complete the 22 CFR 120.41 specially-designed test without them.',
      citations: [
        { authority: 'ITAR', section: '22 CFR 120.41', text: 'Specially designed determination requires parent-system context not present in submission.' },
      ],
      proof: { steps: ['component(impeller).', 'gap(parent_system, "unspecified").', 'gap(end_use, "unspecified").', 'escalate :- gap(parent_system) ; gap(end_use).'] },
      regimes: ['usml'],
    },
  };

  document.querySelectorAll('button[data-example]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const key = btn.dataset.example;
      input.value = EXAMPLES[key] || '';
      input.focus();
      // Render preloaded result immediately
      if (PRELOADED[key]) renderResult(PRELOADED[key]);
    });
  });

  function renderResult(payload) {
    if (!payload) return;
    const dec = (payload.decision || 'UNKNOWN').toLowerCase();
    const conf = typeof payload.confidence === 'number'
      ? Math.round(payload.confidence * 100) + '%'
      : 'n/a';

    const proofSteps = (payload.proof?.steps || [])
      .slice(0, 6)
      .map((s, i) => `${i + 1}. ${typeof s === 'string' ? s : (s.conclusion || JSON.stringify(s))}`)
      .join('\n');

    const citations = (payload.citations || [])
      .slice(0, 3)
      .map((c) => `&middot; ${c.authority || ''} ${c.section || ''}`)
      .join('<br>');

    const regimes = (payload.regimes || []).join(', ') || '(none fired)';

    result.style.color = 'var(--text-primary)';
    result.style.alignItems = 'flex-start';
    result.style.justifyContent = 'flex-start';
    result.style.textAlign = 'left';
    result.innerHTML = `
      <div style="width: 100%;">
        <div style="text-align: center; margin-bottom: var(--space-5);">
          <div class="decision-badge ${dec}" style="font-size: 1rem; padding: var(--space-3) var(--space-6);">
            ${payload.decision || 'UNKNOWN'}
          </div>
          <div class="mono-tag mt-2">Confidence: ${conf} &middot; Regimes: ${regimes}</div>
        </div>

        ${payload.rationale ? `
          <div style="margin-bottom: var(--space-4);">
            <div class="text-mono text-uppercase text-secondary text-xs mb-2">Rationale</div>
            <div style="font-size: var(--fs-sm); line-height: var(--lh-snug); color: var(--text-primary); font-family: var(--font-sans);">
              ${escapeHtml(payload.rationale)}
            </div>
          </div>` : ''}

        ${citations ? `
          <div style="margin-bottom: var(--space-4);">
            <div class="text-mono text-uppercase text-secondary text-xs mb-2">Citations</div>
            <div style="font-size: var(--fs-xs); color: var(--text-secondary);">${citations}</div>
          </div>` : ''}

        ${proofSteps ? `
          <div>
            <div class="text-mono text-uppercase text-secondary text-xs mb-2">Proof tree (first 6 steps)</div>
            <pre style="font-size: var(--fs-xs); color: var(--text-secondary); margin: 0; white-space: pre-wrap; line-height: 1.5;">${escapeHtml(proofSteps)}</pre>
          </div>` : ''}
      </div>
    `;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  }

  function renderError(msg) {
    result.style.color = 'var(--accent-danger)';
    result.style.alignItems = 'center';
    result.style.justifyContent = 'center';
    result.style.textAlign = 'center';
    result.innerHTML = `
      <div>
        <div class="text-mono text-uppercase text-xs mb-2">Request failed</div>
        <div style="font-size: var(--fs-sm);">${escapeHtml(msg)}</div>
        <div class="mono-tag mt-3">Make sure the FastAPI server is running at /api/analyze</div>
      </div>
    `;
  }

  if (runBtn) {
    runBtn.addEventListener('click', async () => {
      const artifact = (input?.value || '').trim();
      if (!artifact) {
        renderError('Paste an artifact first.');
        return;
      }

      runBtn.disabled = true;
      runText.innerHTML = '<span class="spinner-tactical" style="width: 12px; height: 12px;"></span>&nbsp;&nbsp;Analyzing';

      try {
        const res = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ artifact, type: 'protocol' }),
        });

        if (!res.ok) {
          throw new Error(`HTTP ${res.status} ${res.statusText}`);
        }

        const payload = await res.json();
        renderResult(payload);
      } catch (err) {
        renderError(err.message || String(err));
      } finally {
        runBtn.disabled = false;
        runText.textContent = 'Analyze';
      }
    });
  }
})();
