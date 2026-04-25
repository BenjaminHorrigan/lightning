// Agent Explorer — D3 tree visualization with live LIGHTNING checks

const COLORS = {
    root:     '#8b5cf6',
    branch:   '#6366f1',
    pending:  '#374151',
    checking: '#3b82f6',
    ALLOW:    '#22c55e',
    REFUSE:   '#ef4444',
    ESCALATE: '#f59e0b',
};

const NODE_R = { root: 24, branch: 18, leaf: 15 };

let nodeResults = {};   // leaf_id → {decision, rationale, controlled_elements}
let currentTopic = 'Design a propulsion system for a 3U CubeSat research satellite';

// ─── Init ────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    // Scenario buttons
    document.querySelectorAll('.scenario-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.scenario-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            if (btn.dataset.topic === 'custom') {
                document.getElementById('custom-row').style.removeProperty('display');
            } else {
                document.getElementById('custom-row').style.display = 'none !important';
                currentTopic = btn.dataset.topic;
            }
        });
    });

    document.getElementById('custom-input').addEventListener('input', e => {
        currentTopic = e.target.value.trim() || currentTopic;
    });

    document.getElementById('run-btn').addEventListener('click', runExploration);
});

// ─── Main flow ───────────────────────────────────────────────────────────────

async function runExploration() {
    const topic = currentTopic;
    if (!topic) return;

    // Reset
    nodeResults = {};
    document.getElementById('run-btn').disabled = true;
    document.getElementById('graph-container').innerHTML = '';
    document.getElementById('detail-panel').textContent = 'Click any leaf node to see the LIGHTNING decision and rationale.';
    document.getElementById('detail-node-label').textContent = '';
    setStatus('Generating research pathways…', 'standby');
    setCounters(null);

    try {
        const response = await fetch('/api/agent-explore', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic }),
        });

        if (!response.ok) {
            const err = await response.json();
            setStatus('Error: ' + (err.detail || 'unknown'), 'danger');
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let currentEvent = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();   // keep incomplete line

            for (const line of lines) {
                if (line.startsWith('event:')) {
                    currentEvent = line.slice(6).trim();
                } else if (line.startsWith('data:') && line.length > 5) {
                    try {
                        const data = JSON.parse(line.slice(5).trim());
                        handleEvent(currentEvent, data);
                    } catch (_) { /* skip malformed */ }
                }
            }
        }
    } catch (err) {
        setStatus('Network error: ' + err.message, 'danger');
    } finally {
        document.getElementById('run-btn').disabled = false;
    }
}

function handleEvent(type, data) {
    switch (type) {
        case 'status':
            setStatus(data.message, 'standby');
            break;
        case 'tree':
            renderTree(data);
            setStatus('Running compliance checks in parallel…', 'active');
            break;
        case 'checking':
            pulseNode(data.node_id);
            break;
        case 'result':
            nodeResults[data.node_id] = data;
            updateNode(data.node_id, data.decision, data.rationale);
            updateCounters();
            break;
        case 'done':
            setStatus('Analysis complete', 'verified');
            break;
        case 'error':
            setStatus('Error: ' + data.message, 'danger');
            break;
    }
}

// ─── D3 tree ─────────────────────────────────────────────────────────────────

function toHierarchy(data) {
    return {
        id: 'root', label: data.root_label, type: 'root',
        children: (data.branches || []).map(b => ({
            id: b.id, label: b.label, type: 'branch',
            children: (b.leaves || []).map(l => ({
                id: l.id, label: l.label, type: 'leaf', artifact: l.artifact,
            })),
        })),
    };
}

function renderTree(data) {
    const container = document.getElementById('graph-container');
    const W = Math.max(container.clientWidth || 700, 700);
    const margin = { top: 50, right: 20, bottom: 60, left: 20 };

    // Estimate height from leaf count
    const leafCount = (data.branches || []).reduce((s, b) => s + (b.leaves || []).length, 0);
    const H = Math.max(420, leafCount * 72 + margin.top + margin.bottom);

    const svg = d3.select('#graph-container')
        .append('svg')
        .attr('width', '100%')
        .attr('viewBox', `0 0 ${W} ${H}`)
        .attr('preserveAspectRatio', 'xMidYMid meet');

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
    const iW = W - margin.left - margin.right;
    const iH = H - margin.top - margin.bottom;

    const root = d3.hierarchy(toHierarchy(data));
    d3.tree().size([iW, iH])(root);

    // Links
    g.selectAll('.tree-link')
        .data(root.links())
        .join('path')
        .attr('class', 'tree-link')
        .attr('d', d3.linkVertical().x(d => d.x).y(d => d.y))
        .style('opacity', 0)
        .transition().delay((_, i) => i * 60).duration(300)
        .style('opacity', 1);

    // Node groups
    const node = g.selectAll('.tree-node')
        .data(root.descendants())
        .join('g')
        .attr('class', 'tree-node')
        .attr('id', d => `ng-${d.data.id}`)
        .attr('transform', d => `translate(${d.x},${d.y})`)
        .style('opacity', 0)
        .style('cursor', d => d.data.type === 'leaf' ? 'pointer' : 'default')
        .on('click', (_, d) => { if (d.data.type === 'leaf') showDetail(d.data); });

    node.transition().delay((_, i) => i * 80).duration(300).style('opacity', 1);

    // Pulse ring (leaf only)
    node.filter(d => d.data.type === 'leaf')
        .append('circle')
        .attr('class', 'pulse-ring')
        .attr('r', NODE_R.leaf)
        .attr('stroke', 'transparent')
        .attr('fill', 'none');

    // Main circle
    node.append('circle')
        .attr('class', 'node-circle')
        .attr('id', d => `nc-${d.data.id}`)
        .attr('r', d => NODE_R[d.data.type] || NODE_R.leaf)
        .attr('fill', d => d.data.type === 'leaf' ? COLORS.pending : COLORS[d.data.type])
        .attr('stroke', '#0f172a')
        .attr('stroke-width', 2);

    // Labels (two lines for long text)
    const labelY = d => (NODE_R[d.data.type] || NODE_R.leaf) + 14;

    node.each(function(d) {
        const grp = d3.select(this);
        const words = d.data.label.split(' ');
        const isRoot = d.data.type === 'root';
        const cls = isRoot ? 'node-root' : 'node-label';
        const mid = Math.ceil(words.length / 2);
        const line1 = words.slice(0, mid).join(' ');
        const line2 = words.slice(mid).join(' ');

        const txt = grp.append('text').attr('class', cls).attr('text-anchor', 'middle');

        if (line2) {
            txt.append('tspan').attr('x', 0).attr('dy', labelY(d)).text(line1);
            txt.append('tspan').attr('x', 0).attr('dy', '1.2em').text(line2);
        } else {
            txt.append('tspan').attr('x', 0).attr('dy', labelY(d)).text(line1);
        }
    });
}

// ─── Node state updates ───────────────────────────────────────────────────────

function pulseNode(nodeId) {
    const ring = d3.select(`#ng-${nodeId} .pulse-ring`);
    if (ring.empty()) return;

    (function pulse() {
        ring.attr('r', NODE_R.leaf).attr('stroke', COLORS.checking).attr('stroke-opacity', 0.9)
            .transition().duration(700).ease(d3.easeSinOut)
            .attr('r', NODE_R.leaf + 14).attr('stroke-opacity', 0)
            .on('end', pulse);
    })();
}

function updateNode(nodeId, decision) {
    // Stop pulse
    d3.select(`#ng-${nodeId} .pulse-ring`).interrupt()
        .attr('stroke', 'transparent');

    // Animate fill
    d3.select(`#nc-${nodeId}`)
        .transition().duration(500).ease(d3.easeCubicOut)
        .attr('fill', COLORS[decision] || COLORS.pending);
}

// ─── Detail panel ─────────────────────────────────────────────────────────────

function showDetail(nodeData) {
    const result = nodeResults[nodeData.id];
    const label = document.getElementById('detail-node-label');
    const panel = document.getElementById('detail-panel');

    label.textContent = nodeData.label;

    if (!result) {
        panel.innerHTML = '<span style="color:#6b7280">Check still running…</span>';
        return;
    }

    const badgeCls = `badge-${result.decision}`;
    const controlled = result.controlled_elements && result.controlled_elements.length
        ? `<div class="mt-2" style="color:#9ca3af">Controlled: ${result.controlled_elements.join(', ')}</div>`
        : '';

    panel.innerHTML = `
        <span class="decision-badge ${badgeCls}">${result.decision}</span>
        <span style="color:#6b7280;font-size:11px;margin-left:8px">${(result.confidence * 100).toFixed(0)}% confidence</span>
        <div class="mt-2" style="color:#d1d5db;line-height:1.5">${result.rationale}</div>
        ${controlled}
    `;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function setStatus(msg, pillClass) {
    document.getElementById('status-msg').textContent = msg;
    const pill = document.getElementById('status-pill');
    pill.className = `status-pill ${pillClass || 'standby'}`;
    pill.textContent = pillClass === 'verified' ? 'COMPLETE'
                     : pillClass === 'active'   ? 'RUNNING'
                     : pillClass === 'danger'   ? 'ERROR'
                     : 'STANDBY';
}

function setCounters(val) {
    ['allow', 'refuse', 'escalate'].forEach(k => {
        document.getElementById(`count-${k}`).textContent = val === null ? '—' : '0';
    });
}

function updateCounters() {
    const counts = { ALLOW: 0, REFUSE: 0, ESCALATE: 0 };
    Object.values(nodeResults).forEach(r => { if (counts[r.decision] !== undefined) counts[r.decision]++; });
    document.getElementById('count-allow').textContent    = counts.ALLOW;
    document.getElementById('count-refuse').textContent   = counts.REFUSE;
    document.getElementById('count-escalate').textContent = counts.ESCALATE;
}
