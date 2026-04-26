/* =============================================================================
   admin.js — Lightning Admin Console
   ============================================================================= */

(() => {
  // UI Elements
  const engineStatus = document.getElementById('engine-status');
  const messageBox = document.getElementById('message-box');
  const saveRegimesBtn = document.getElementById('save-regimes');
  const saveThresholdsBtn = document.getElementById('save-thresholds');
  const refreshStatusBtn = document.getElementById('refresh-status');
  
  // Threshold sliders
  const refuseThresholdSlider = document.getElementById('refuse-threshold');
  const allowThresholdSlider = document.getElementById('allow-threshold');
  const crossRegimeSlider = document.getElementById('cross-regime-threshold');
  const refuseValue = document.getElementById('refuse-value');
  const allowValue = document.getElementById('allow-value');
  const crossRegimeValue = document.getElementById('cross-regime-value');

  // Chart instance
  let performanceChart = null;

  function showMessage(msg, type = 'info') {
    const colors = {
      'success': { bg: 'var(--accent-success)', border: 'var(--accent-success)' },
      'error':   { bg: 'var(--accent-danger)',  border: 'var(--accent-danger)'  },
      'warning': { bg: 'var(--accent-warning)', border: 'var(--accent-warning)' },
      'info':    { bg: 'var(--accent-primary)', border: 'var(--accent-primary)' },
    }[type] || { bg: 'var(--accent-primary)', border: 'var(--accent-primary)' };

    // Fixed-position toast so it's visible regardless of scroll position
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 9999;
      background: var(--bg-surface); border: 1px solid ${colors.border};
      color: ${colors.bg}; font-family: var(--font-mono); font-size: 0.82rem;
      padding: 0.75rem 1.25rem; border-radius: 3px; max-width: 360px;
      box-shadow: 0 0 16px ${colors.bg}40; line-height: 1.5;
      animation: fadeInUp 0.2s ease;
    `;
    toast.textContent = msg;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  function setEngineStatus(status, label) {
    engineStatus.className = `status-pill ${status}`;
    engineStatus.textContent = label;
  }

  function updateThresholdDisplay() {
    refuseValue.textContent = Math.round(refuseThresholdSlider.value * 100) + '%';
    allowValue.textContent = Math.round(allowThresholdSlider.value * 100) + '%';
    crossRegimeValue.textContent = crossRegimeSlider.value + (crossRegimeSlider.value == 1 ? ' regime' : ' regimes');
  }

  // Slider event listeners
  refuseThresholdSlider.addEventListener('input', updateThresholdDisplay);
  allowThresholdSlider.addEventListener('input', updateThresholdDisplay);
  crossRegimeSlider.addEventListener('input', updateThresholdDisplay);

  async function loadSystemStatus() {
    try {
      const response = await fetch('/api/admin/status');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();

      // Update system metrics
      document.getElementById('uptime-value').textContent = data.uptime || '4h 27m';
      document.getElementById('rules-loaded').textContent = data.rules_loaded || 85;
      document.getElementById('active-regimes').textContent = data.active_regimes || 3;
      document.getElementById('memory-usage').textContent = data.memory_usage || '247 MB';
      document.getElementById('response-time').textContent = data.response_time || '840ms';

      // Update engine status
      if (data.engine_status === 'online') {
        setEngineStatus('running', 'ENGINE ONLINE');
      } else if (data.engine_status === 'degraded') {
        setEngineStatus('error', 'ENGINE DEGRADED');
      } else {
        setEngineStatus('standby', 'ENGINE OFFLINE');
      }

      // Update regime rule counts
      if (data.regime_counts) {
        document.getElementById('usml-rule-count').textContent = `${data.regime_counts.usml || 42} rules`;
        document.getElementById('cwc-rule-count').textContent = `${data.regime_counts.cwc || 28} rules`;
        document.getElementById('mtcr-rule-count').textContent = `${data.regime_counts.mtcr || 15} rules`;
        document.getElementById('ear-rule-count').textContent = `${data.regime_counts.ear || 0} rules`;
        document.getElementById('dea-rule-count').textContent = `${data.regime_counts.dea || 0} rules`;
        document.getElementById('select-agents-rule-count').textContent = `${data.regime_counts.select_agents || 0} rules`;
      }

      // Update recent activity
      if (data.recent_activity) {
        updateRecentActivity(data.recent_activity);
      }

      // Update performance chart
      if (data.performance_history) {
        updatePerformanceChart(data.performance_history);
      }

      return data;
    } catch (err) {
      showMessage(`Status update failed: ${err.message}`, 'error');
      setEngineStatus('error', 'ENGINE ERROR');
      return null;
    }
  }

  function updateRecentActivity(activities) {
    const container = document.getElementById('recent-activity');
    
    container.innerHTML = activities.slice(0, 4).map(activity => `
      <div class="activity-item">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <span class="decision-badge ${activity.decision.toLowerCase()}">${activity.decision}</span>
          <span class="mono-tag">${activity.timestamp}</span>
        </div>
        <div style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-secondary); line-height: 1.4;">
          ${activity.summary}
        </div>
      </div>
    `).join('');
  }

  function initPerformanceChart() {
    const ctx = document.getElementById('performance-chart');
    if (!ctx) return;

    performanceChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: Array.from({length: 20}, (_, i) => `${16 + Math.floor(i/4)}:${(i%4)*15}`),
        datasets: [{
          label: 'Classifications/min',
          data: [12, 15, 11, 18, 22, 19, 25, 23, 28, 31, 27, 33, 29, 35, 32, 38, 34, 41, 37, 44],
          borderColor: 'rgba(0, 212, 255, 0.8)',
          backgroundColor: 'rgba(0, 212, 255, 0.1)',
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            display: true,
            grid: { color: 'rgba(42, 58, 90, 0.3)' },
            ticks: { 
              color: 'rgba(139, 150, 173, 0.8)',
              font: { family: 'JetBrains Mono', size: 10 }
            }
          },
          y: {
            display: true,
            grid: { color: 'rgba(42, 58, 90, 0.3)' },
            ticks: { 
              color: 'rgba(139, 150, 173, 0.8)',
              font: { family: 'JetBrains Mono', size: 10 }
            }
          }
        },
        interaction: { intersect: false },
        elements: {
          line: { borderWidth: 2 }
        }
      }
    });
  }

  function updatePerformanceChart(historyData) {
    if (!performanceChart || !historyData) return;

    // Update chart with new data
    performanceChart.data.datasets[0].data = historyData.slice(-20);
    performanceChart.update('none'); // No animation for real-time updates
  }

  async function saveRegimeConfiguration() {
    const regimeConfig = {
      usml: {
        enabled: document.getElementById('regime-usml').checked,
        categories: {
          cat_iv: document.getElementById('usml-cat-iv').checked,
          cat_v: document.getElementById('usml-cat-v').checked,
          cat_xiv: document.getElementById('usml-cat-xiv').checked,
          cat_xv: document.getElementById('usml-cat-xv').checked
        }
      },
      cwc: {
        enabled: document.getElementById('regime-cwc').checked,
        schedules: {
          schedule_1: document.getElementById('cwc-schedule-1').checked,
          schedule_2: document.getElementById('cwc-schedule-2').checked,
          schedule_3: document.getElementById('cwc-schedule-3').checked,
          patterns: document.getElementById('cwc-patterns').checked
        }
      },
      mtcr: {
        enabled: document.getElementById('regime-mtcr').checked,
        categories: {
          cat_1: document.getElementById('mtcr-cat-1').checked,
          cat_2: document.getElementById('mtcr-cat-2').checked
        }
      },
      ear: {
        enabled: document.getElementById('regime-ear').checked,
        categories: {
          cat_1: document.getElementById('ear-cat-1').checked,
          cat_4: document.getElementById('ear-cat-4').checked,
          entity_list: document.getElementById('ear-entity-list').checked
        }
      },
      dea: {
        enabled: document.getElementById('regime-dea').checked,
        schedules: {
          schedule_i: document.getElementById('dea-schedule-i').checked,
          schedule_ii: document.getElementById('dea-schedule-ii').checked,
          precursors: document.getElementById('dea-precursors').checked
        }
      },
      select_agents: {
        enabled: document.getElementById('regime-select-agents').checked,
        sources: {
          hhs: document.getElementById('hhs-select').checked,
          usda: document.getElementById('usda-select').checked,
          australia_group: document.getElementById('australia-group').checked
        }
      }
    };

    saveRegimesBtn.disabled = true;
    saveRegimesBtn.innerHTML = '<span class="spinner-tactical d-inline-block align-middle me-2" style="width:12px;height:12px;border-width:1.5px;"></span>Applying';

    try {
      const response = await fetch('/api/admin/regimes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(regimeConfig)
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();

      if (result.success) {
        showMessage(`✓ Regime configuration updated. ${result.rules_loaded} rules loaded.`, 'success');
        setEngineStatus('running', 'ENGINE ONLINE');
        
        // Refresh status to show updated rule counts
        setTimeout(loadSystemStatus, 500);
      } else {
        throw new Error(result.error || 'Configuration failed');
      }
    } catch (err) {
      showMessage(`Configuration failed: ${err.message}`, 'error');
      setEngineStatus('error', 'CONFIG ERROR');
    } finally {
      saveRegimesBtn.disabled = false;
      saveRegimesBtn.textContent = 'Apply Changes';
    }
  }

  async function saveThresholdConfiguration() {
    const thresholdConfig = {
      refuse_threshold: parseFloat(refuseThresholdSlider.value),
      allow_threshold: parseFloat(allowThresholdSlider.value),
      cross_regime_threshold: parseInt(crossRegimeSlider.value),
      extraction_model: document.getElementById('extraction-model').value,
      features: {
        counterfactuals: document.getElementById('enable-counterfactuals').checked,
        interactive_queries: document.getElementById('enable-interactive-queries').checked,
        cross_regime: document.getElementById('enable-cross-regime').checked,
        audit_log: document.getElementById('enable-audit-log').checked,
        proof_graph: document.getElementById('enable-proof-graph').checked,
        debug_mode: document.getElementById('debug-mode').checked
      }
    };

    saveThresholdsBtn.disabled = true;
    saveThresholdsBtn.innerHTML = '<span class="spinner-tactical d-inline-block align-middle me-2" style="width:12px;height:12px;border-width:1.5px;"></span>Applying';

    try {
      const response = await fetch('/api/admin/thresholds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(thresholdConfig)
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();

      if (result.success) {
        showMessage('✓ Decision thresholds updated successfully.', 'success');
      } else {
        throw new Error(result.error || 'Threshold update failed');
      }
    } catch (err) {
      showMessage(`Threshold update failed: ${err.message}`, 'error');
    } finally {
      saveThresholdsBtn.disabled = false;
      saveThresholdsBtn.textContent = 'Apply Changes';
    }
  }

  // Event listeners
  saveRegimesBtn.addEventListener('click', saveRegimeConfiguration);
  saveThresholdsBtn.addEventListener('click', saveThresholdConfiguration);
  refreshStatusBtn.addEventListener('click', loadSystemStatus);

  // Regime toggle dependencies
  document.getElementById('regime-usml').addEventListener('change', (e) => {
    const subcats = document.querySelectorAll('#usml-subcats input');
    subcats.forEach(input => input.disabled = !e.target.checked);
  });

  document.getElementById('regime-cwc').addEventListener('change', (e) => {
    const subcats = document.querySelectorAll('#cwc-subcats input');
    subcats.forEach(input => input.disabled = !e.target.checked);
  });

  document.getElementById('regime-mtcr').addEventListener('change', (e) => {
    const subcats = document.querySelectorAll('#mtcr-subcats input');
    subcats.forEach(input => input.disabled = !e.target.checked);
  });

  document.getElementById('regime-ear').addEventListener('change', (e) => {
    const subcats = document.querySelectorAll('#ear-subcats input');
    subcats.forEach(input => input.disabled = !e.target.checked);
  });

  document.getElementById('regime-dea').addEventListener('change', (e) => {
    const subcats = document.querySelectorAll('#dea-subcats input');
    subcats.forEach(input => input.disabled = !e.target.checked);
  });

  document.getElementById('regime-select-agents').addEventListener('change', (e) => {
    const subcats = document.querySelectorAll('#select-agents-subcats input');
    subcats.forEach(input => input.disabled = !e.target.checked);
  });

  // Auto-refresh status every 30 seconds
  function startAutoRefresh() {
    setInterval(() => {
      loadSystemStatus();
    }, 30000);
  }

  // Initialize
  updateThresholdDisplay();
  initPerformanceChart();
  loadSystemStatus();
  startAutoRefresh();

  // Add some visual feedback for regime toggles
  const allRegimeCheckboxes = document.querySelectorAll('input[id^="regime-"]');
  allRegimeCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', (e) => {
      const regimeGroup = e.target.closest('.regime-control-group');
      if (regimeGroup) {
        if (e.target.checked) {
          regimeGroup.style.opacity = '1.0';
          regimeGroup.style.borderLeft = '2px solid var(--accent-primary)';
        } else {
          regimeGroup.style.opacity = '0.6';
          regimeGroup.style.borderLeft = '2px solid var(--border-subtle)';
        }
      }
    });
  });
})();
