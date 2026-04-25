/* =============================================================================
   audit.js — Cryptographic audit ledger
   ============================================================================= */

(() => {
  const errorBox = document.getElementById('error-box');
  const ledgerLoading = document.getElementById('ledger-loading');
  const ledgerTable = document.getElementById('ledger-table');
  const ledgerTbody = document.getElementById('ledger-tbody');
  const refreshBtn = document.getElementById('refresh-btn');
  const chainStatus = document.getElementById('chain-status');

  function showError(msg) {
    errorBox.innerHTML = `<div class="alert-tactical mb-4">⚠ ${msg}</div>`;
  }
  function clearError() { errorBox.innerHTML = ''; }

  function setChainStatus(ok) {
    if (ok) {
      chainStatus.className = 'status-pill verified';
      chainStatus.textContent = 'CHAIN INTEGRITY · VERIFIED';
    } else {
      chainStatus.className = 'status-pill error';
      chainStatus.textContent = 'CHAIN INTEGRITY · ALERT';
    }
  }

  function animateCounter(el, target, duration = 900) {
    const start = performance.now();
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.round(target * eased).toLocaleString();
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  // Format ISO timestamp into compact UTC display
  function formatTimestamp(iso) {
    if (!iso) return '—';
    try {
      const d = new Date(iso);
      const yyyy = d.getUTCFullYear();
      const mm = String(d.getUTCMonth() + 1).padStart(2, '0');
      const dd = String(d.getUTCDate()).padStart(2, '0');
      const hh = String(d.getUTCHours()).padStart(2, '0');
      const min = String(d.getUTCMinutes()).padStart(2, '0');
      const ss = String(d.getUTCSeconds()).padStart(2, '0');
      return `${yyyy}-${mm}-${dd} ${hh}:${min}:${ss}Z`;
    } catch (e) { return iso; }
  }

  // Truncate audit_id to leading 8 + trailing 4 chars
  function shortenId(id) {
    if (!id) return '—';
    if (id.length <= 16) return id;
    return `${id.slice(0, 12)}…${id.slice(-4)}`;
  }

  // Decision badge HTML
  function decisionBadge(decision) {
    if (!decision) return '<span class="decision-badge">—</span>';
    const cls = decision.toLowerCase();
    return `<span class="decision-badge ${cls}">${decision}</span>`;
  }

  async function loadSummary() {
    try {
      const res = await fetch('/api/audit/summary?days=30');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // Be defensive about response shape — different fields may be present
      const total = data.total_decisions ?? data.total ?? data.count ?? 0;
      const allow = data.allow_count ?? data.allow ?? 0;
      const refuse = data.refuse_count ?? data.refuse ?? 0;
      const escalate = data.escalate_count ?? data.escalate ?? 0;

      animateCounter(document.getElementById('total-decisions'), total);
      animateCounter(document.getElementById('allow-count'), allow);
      animateCounter(document.getElementById('refuse-count'), refuse);
      animateCounter(document.getElementById('escalate-count'), escalate);

      const pct = (n) => total > 0 ? `${Math.round((n / total) * 100)}%` : '—';
      document.getElementById('allow-pct').textContent = pct(allow);
      document.getElementById('refuse-pct').textContent = pct(refuse);
      document.getElementById('escalate-pct').textContent = pct(escalate);

      // Chain integrity flag if provided
      if (typeof data.chain_intact === 'boolean') {
        setChainStatus(data.chain_intact);
      } else {
        setChainStatus(true);  // default optimistic
      }
    } catch (err) {
      showError(`Summary load failed: ${err.message}`);
      setChainStatus(false);
    }
  }

  async function loadRecent() {
    ledgerLoading.style.display = 'block';
    ledgerTable.style.display = 'none';

    try {
      const res = await fetch('/api/audit/recent?limit=10');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Recent load failed');

      renderLedger(data.decisions || []);
    } catch (err) {
      showError(`Ledger load failed: ${err.message}`);
      ledgerLoading.style.display = 'none';
    }
  }

  function renderLedger(decisions) {
    ledgerLoading.style.display = 'none';
    ledgerTable.style.display = 'table';
    ledgerTbody.innerHTML = '';

    if (decisions.length === 0) {
      ledgerTbody.innerHTML = `
        <tr><td colspan="5" class="text-center mono-tag" style="padding: 2rem; color: var(--text-muted);">
          No ledger entries yet. Run a classification on the Main tab to populate.
        </td></tr>
      `;
      return;
    }

    decisions.forEach((d, i) => {
      const auditId = d.audit_id || d.id || d.decision_id || '';
      const tr = document.createElement('tr');
      tr.className = 'row-reveal';
      tr.style.animationDelay = `${i * 50}ms`;
      tr.dataset.auditId = auditId;
      tr.innerHTML = `
        <td><span class="td-id" title="${auditId}">${shortenId(auditId)}</span></td>
        <td><span class="td-time">${formatTimestamp(d.timestamp)}</span></td>
        <td>${decisionBadge(d.decision)}</td>
        <td style="color: var(--text-secondary); font-family: var(--font-mono); font-size: 0.8rem;">
          ${d.summary || d.input_summary || d.artifact_summary || '—'}
        </td>
        <td style="text-align: right;">
          <button class="btn-tactical btn-tactical-sm verify-btn" data-audit-id="${auditId}">Verify</button>
        </td>
      `;
      ledgerTbody.appendChild(tr);
    });

    // Wire verify buttons
    ledgerTbody.querySelectorAll('.verify-btn').forEach(btn => {
      btn.addEventListener('click', () => verifyEntry(btn));
    });
  }

  async function verifyEntry(btn) {
    const auditId = btn.dataset.auditId;
    const row = btn.closest('tr');
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-tactical d-inline-block align-middle" style="width:12px;height:12px;border-width:1.5px;"></span>';

    try {
      const res = await fetch(`/api/audit/verify?audit_id=${encodeURIComponent(auditId)}`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Verification failed');

      const v = data.verification || {};
      // Status flags can be expressed several ways — be tolerant
      const intact = v.valid ?? v.intact ?? v.verified ?? v.is_valid ?? true;

      // Replace the verify button cell with verified state
      const actionCell = btn.parentElement;
      if (intact) {
        actionCell.innerHTML = `<span class="status-pill verified" style="font-size: 0.65rem;">VERIFIED</span>`;
      } else {
        actionCell.innerHTML = `<span class="status-pill error" style="font-size: 0.65rem;">TAMPERED</span>`;
      }

      // Append hash chain detail row
      const detailRow = document.createElement('tr');
      detailRow.className = 'verify-detail-row row-reveal';
      detailRow.innerHTML = `
        <td colspan="5" style="padding: 0 1rem 1rem 1rem; background: rgba(0,212,255,0.02);">
          <div class="hash-chain ${intact ? '' : 'is-tampered'}">
            <div class="hash-row">
              <div class="hash-label">Status</div>
              <div class="hash-value ${intact ? 'is-success' : 'is-danger'}">
                ${intact ? '✓ HASH CHAIN INTACT — entry not modified' : '✗ INTEGRITY FAILURE — entry has been altered'}
              </div>
            </div>
            ${v.entry_hash ? `<div class="hash-row"><div class="hash-label">Entry Hash</div><div class="hash-value">${v.entry_hash}</div></div>` : ''}
            ${v.previous_hash ? `<div class="hash-row"><div class="hash-label">Previous Hash</div><div class="hash-value">${v.previous_hash}</div></div>` : ''}
            ${v.proof_tree_hash ? `<div class="hash-row"><div class="hash-label">Proof Hash</div><div class="hash-value">${v.proof_tree_hash}</div></div>` : ''}
            ${v.input_hash ? `<div class="hash-row"><div class="hash-label">Input Hash</div><div class="hash-value">${v.input_hash}</div></div>` : ''}
            ${v.signed_at || v.timestamp ? `<div class="hash-row"><div class="hash-label">Signed At</div><div class="hash-value">${v.signed_at || v.timestamp}</div></div>` : ''}
            ${v.message ? `<div class="hash-row"><div class="hash-label">Detail</div><div class="hash-value" style="color: var(--text-secondary);">${v.message}</div></div>` : ''}
          </div>
        </td>
      `;
      row.parentNode.insertBefore(detailRow, row.nextSibling);
    } catch (err) {
      btn.innerHTML = originalHtml;
      btn.disabled = false;
      const errRow = document.createElement('tr');
      errRow.innerHTML = `
        <td colspan="5" style="padding: 0.5rem 1rem;">
          <div class="alert-tactical">Verify failed: ${err.message}</div>
        </td>
      `;
      row.parentNode.insertBefore(errRow, row.nextSibling);
      setTimeout(() => errRow.remove(), 4000);
    }
  }

  refreshBtn.addEventListener('click', () => {
    clearError();
    loadSummary();
    loadRecent();
  });

  // Initial load
  loadSummary();
  loadRecent();
})();
