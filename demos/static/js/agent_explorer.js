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
const TRUNC  = { root: 999, branch: 22, leaf: 18 };   // chars before truncation

function trunc(s, type) {
    const max = TRUNC[type] || 18;
    return s.length > max ? s.slice(0, max) + '…' : s;
}

let nodeResults = {};   // leaf_id → {decision, rationale, controlled_elements}
let currentTopic = 'Design a propulsion system for a 3U CubeSat research satellite';

// ─── Init ────────────────────────────────────────────────────────────────────

// ── Pre-computed demo tree ────────────────────────────────────────────────────

const DEMO_TREE = {
    root_label: 'Design and ground-test a propulsion system for a 3U CubeSat research mission',
    branches: [
        {
            id: 'branch_0', label: 'Chemical propulsion',
            leaves: [
                { id: 'leaf_0_0', label: 'Hydrazine monoprop',        artifact: 'Hydrazine (N2H4) monopropellant thruster, 1N thrust, Isp 220s, titanium tank, heritage design for LEO CubeSat. Parent system: 3U research satellite propulsion bus.' },
                { id: 'leaf_0_1', label: 'Butane cold-gas',           artifact: 'Butane cold-gas thruster, 0.1N thrust, Isp 65s, MEMS micro-valve. Attitude control on 3U CubeSat LEO mission.' },
                { id: 'leaf_0_2', label: 'AF-M315E green prop',       artifact: 'AF-M315E (hydroxyl ammonium nitrate) green monopropellant, 1N thruster, Isp 250s. Hydrazine replacement.' },
                { id: 'leaf_0_3', label: 'H2O2 90% monoprop',         artifact: 'High-test hydrogen peroxide (90% concentration) catalyst-pack monopropellant thruster, 0.5N thrust.' },
            ],
        },
        {
            id: 'branch_1', label: 'Electric propulsion',
            leaves: [
                { id: 'leaf_1_0', label: 'Iodine ion thruster',       artifact: 'Iodine-propellant gridded ion thruster, 0.8 mN, Isp 2000s, 40W. Orbit maintenance on 3U CubeSat.' },
                { id: 'leaf_1_1', label: 'FEEP electrospray',         artifact: 'Field-emission electrospray propulsion (FEEP), ionic liquid propellant, 0.1 mN, Isp 5000s.' },
                { id: 'leaf_1_2', label: 'Xenon Hall thruster',       artifact: 'Xenon Hall-effect thruster, 10 mN, Isp 1500s, 200W. Parent: research CubeSat constellation, 12 satellites.' },
            ],
        },
        {
            id: 'branch_2', label: 'Solid propulsion',
            leaves: [
                { id: 'leaf_2_0', label: 'APCP solid grain',          artifact: 'Ammonium perchlorate composite propellant grain, 50g loading, end-burner geometry. Parent: experimental CubeSat propulsion test article.' },
                { id: 'leaf_2_1', label: 'HTPB binder system',        artifact: 'HTPB (hydroxyl-terminated polybutadiene) binder, 1 kg, for composite propellant fabrication research.' },
                { id: 'leaf_2_2', label: 'Black powder igniter',      artifact: 'Black powder pyrotechnic igniter charge, 1g, ATF-licensed manufacturer, sealed assembly.' },
            ],
        },
        {
            id: 'branch_3', label: 'Propellantless',
            leaves: [
                { id: 'leaf_3_0', label: 'Solar sail',                artifact: 'Mylar solar sail, 4m² deployed area, 3U stowage volume. LEO-to-GEO transfer.' },
                { id: 'leaf_3_1', label: 'Reaction wheels',           artifact: 'Reaction wheel assembly, 3-axis attitude, 30 mNms momentum, magnetic-torquer desaturation.' },
            ],
        },
        {
            id: 'branch_4', label: 'Procurement',
            leaves: [
                { id: 'leaf_4_0', label: 'Foreign hydrazine vendor',  artifact: 'Source 500 mL anhydrous hydrazine from European industrial supplier (Veonika GmbH, Germany) for ground-test campaign.' },
                { id: 'leaf_4_1', label: 'US butane bulk supplier',   artifact: 'Procure 5 L research-grade butane from a domestic gas supplier (Airgas).' },
                { id: 'leaf_4_2', label: 'Iodine pellets',            artifact: 'Procure 100 g iodine pellets, research-grade, from US chemical distributor.' },
            ],
        },
        {
            id: 'branch_5', label: 'Test infrastructure',
            leaves: [
                { id: 'leaf_5_0', label: 'Thrust balance fixture',    artifact: 'Pendulum thrust balance, 1 µN resolution, in-house fabrication, no controlled components.' },
                { id: 'leaf_5_1', label: 'Vacuum chamber rental',     artifact: 'Rent 1 m diameter vacuum chamber, 1e-5 torr, university test facility, on-campus use.' },
                { id: 'leaf_5_2', label: 'Foreign collab data share', artifact: 'Share thruster performance data and CFD simulation results with German research partner (Veonika GmbH) for joint publication.' },
            ],
        },
    ],
};

const DEMO_RESULTS = {
    // Chemical
    leaf_0_0: { decision: 'REFUSE',   confidence: 0.97, rationale: 'Hydrazine (N₂H₄) for satellite propulsion triggers USML IV(h)(1) — liquid propellants specially designed for spacecraft propulsion systems.', controlled_elements: ['hydrazine'] },
    leaf_0_1: { decision: 'ALLOW',    confidence: 0.99, rationale: 'Butane cold-gas system. No controlled substance, no USML/CWC/MTCR match. Standard commercial CubeSat component.',                              controlled_elements: [] },
    leaf_0_2: { decision: 'ESCALATE', confidence: 0.71, rationale: 'AF-M315E (HAN-based) is not on current controlled substance lists but is an energetic ionic liquid. Classification depends on export destination and end-user.', controlled_elements: [] },
    leaf_0_3: { decision: 'ESCALATE', confidence: 0.74, rationale: 'High-test hydrogen peroxide (>70%) is dual-use: regulated under EAR for export, unrestricted for domestic research at gram-scale. End-use verification required.', controlled_elements: ['hydrogen_peroxide_high_test'] },

    // Electric
    leaf_1_0: { decision: 'ALLOW',    confidence: 0.95, rationale: 'Iodine ion thruster. Iodine is not a controlled propellant. Electric propulsion at this thrust level does not trigger MTCR range/payload thresholds.', controlled_elements: [] },
    leaf_1_1: { decision: 'ALLOW',    confidence: 0.97, rationale: 'FEEP electrospray with ionic liquid propellant. No controlled substance match. Precision attitude propulsion within commercial CubeSat norms.', controlled_elements: [] },
    leaf_1_2: { decision: 'ESCALATE', confidence: 0.68, rationale: 'Xenon Hall thrusters are commercial; however, "research CubeSat constellation, 12 satellites" raises USML Cat IV(h) specially-designed inheritance questions. Manual review of constellation end-use required.', controlled_elements: [] },

    // Solid
    leaf_2_0: { decision: 'REFUSE',   confidence: 0.94, rationale: 'Ammonium perchlorate composite propellant grain triggers USML Cat V(b) — solid propellants and energetic-material formulations.', controlled_elements: ['ammonium_perchlorate', 'apcp'] },
    leaf_2_1: { decision: 'ESCALATE', confidence: 0.62, rationale: 'HTPB is dual-use: tire-industry binder AND composite-propellant binder. 1 kg is plausible for either. End-use disclosure (propellant fabrication) shifts toward USML Cat V via specially-designed inheritance.', controlled_elements: ['htpb'] },
    leaf_2_2: { decision: 'ALLOW',    confidence: 0.91, rationale: 'Black powder igniter, 1g, from ATF-licensed manufacturer in sealed assembly. ATF licensing is the controlling authority and is satisfied.', controlled_elements: [] },

    // Propellantless
    leaf_3_0: { decision: 'ALLOW',    confidence: 0.99, rationale: 'Solar sail — propellantless. No controlled substance, no USML/MTCR trigger. Standard research spacecraft technology.', controlled_elements: [] },
    leaf_3_1: { decision: 'ALLOW',    confidence: 0.99, rationale: 'Reaction wheel attitude control — propellantless. No controlled elements. Standard commercial spacecraft component.', controlled_elements: [] },

    // Procurement
    leaf_4_0: { decision: 'REFUSE',   confidence: 0.96, rationale: 'Foreign procurement of hydrazine triggers DFARS 252.225 (foreign-source restriction) compounded with USML IV(h)(1) on the substance itself. Not the right path.', controlled_elements: ['hydrazine'] },
    leaf_4_1: { decision: 'ALLOW',    confidence: 0.99, rationale: 'Domestic butane supply from Airgas. No controlled substance, no foreign-source concern. Standard procurement.', controlled_elements: [] },
    leaf_4_2: { decision: 'ALLOW',    confidence: 0.97, rationale: 'Iodine is not a controlled chemical at this quantity. US distributor satisfies any sourcing requirements.', controlled_elements: [] },

    // Test infrastructure
    leaf_5_0: { decision: 'ALLOW',    confidence: 0.99, rationale: 'Pendulum thrust balance, in-house fabrication, no controlled components. Pure measurement instrument.', controlled_elements: [] },
    leaf_5_1: { decision: 'ALLOW',    confidence: 0.98, rationale: 'On-campus vacuum chamber rental for ground-test. No export/transfer of controlled technology.', controlled_elements: [] },
    leaf_5_2: { decision: 'REFUSE',   confidence: 0.93, rationale: 'Sharing CFD and thruster performance data with foreign national triggers ITAR §120.6 (controlled technical data) and §120.17 (deemed export). Use export-licensed channels only.', controlled_elements: ['technical_data'] },
};

function loadDemo() {
    nodeResults = {};
    document.getElementById('graph-container').innerHTML = '';
    document.getElementById('detail-panel').textContent = 'Click any leaf node to see the LIGHTNING decision.';
    document.getElementById('detail-node-label').textContent = '';
    setCounters(null);
    setStatus('Rendering demo tree…', 'standby');

    renderTree(DEMO_TREE);

    // Apply all results with staggered animation
    const leaves = Object.keys(DEMO_RESULTS);
    leaves.forEach((id, i) => {
        setTimeout(() => {
            const r = DEMO_RESULTS[id];
            nodeResults[id] = r;
            updateNode(id, r.decision, r.rationale);
            updateCounters();
            if (i === leaves.length - 1) setStatus('Analysis complete (preloaded)', 'verified');
        }, 200 + i * 180);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const demoBtn = document.getElementById('demo-btn');
    if (demoBtn) demoBtn.addEventListener('click', loadDemo);

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

    // ── Embed mode: ?embed=true hides chrome and auto-runs the preloaded demo
    if (new URLSearchParams(window.location.search).get('embed') === 'true') {
        document.body.classList.add('embed-mode');
        // Run the demo as soon as fonts/layout settle so it's already animating
        // when the slide becomes visible.
        setTimeout(loadDemo, 200);
    }
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

    const tooltip = document.getElementById('node-tooltip');
    const graphRect = () => document.getElementById('graph-container').getBoundingClientRect();

    // Node groups
    const node = g.selectAll('.tree-node')
        .data(root.descendants())
        .join('g')
        .attr('class', 'tree-node')
        .attr('id', d => `ng-${d.data.id}`)
        .attr('transform', d => `translate(${d.x},${d.y})`)
        .style('opacity', 0)
        .style('cursor', d => d.data.type === 'leaf' ? 'pointer' : 'default')
        .on('click', (_, d) => { if (d.data.type === 'leaf') showDetail(d.data); })
        .on('mouseover', function(event, d) {
            // Raise to front so label isn't clipped by siblings
            d3.select(this).raise();
            // Show tooltip with full label
            tooltip.textContent = d.data.label;
            tooltip.style.display = 'block';
            const gr = graphRect();
            tooltip.style.left = (event.clientX - gr.left + 12) + 'px';
            tooltip.style.top  = (event.clientY - gr.top  - 10) + 'px';
        })
        .on('mousemove', function(event) {
            const gr = graphRect();
            tooltip.style.left = (event.clientX - gr.left + 12) + 'px';
            tooltip.style.top  = (event.clientY - gr.top  - 10) + 'px';
        })
        .on('mouseout', () => { tooltip.style.display = 'none'; });

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
        const isRoot = d.data.type === 'root';
        const cls = isRoot ? 'node-root' : 'node-label';
        const truncated = trunc(d.data.label, d.data.type);
        const words = truncated.split(' ');
        const mid = Math.ceil(words.length / 2);
        const line1 = words.slice(0, mid).join(' ');
        const line2 = words.slice(mid).join(' ');

        const txt = grp.append('text').attr('class', cls).attr('text-anchor', 'middle');

        if (line2 && d.data.type !== 'root') {
            txt.append('tspan').attr('x', 0).attr('dy', labelY(d)).text(line1);
            txt.append('tspan').attr('x', 0).attr('dy', '1.2em').text(line2);
        } else {
            txt.append('tspan').attr('x', 0).attr('dy', labelY(d)).text(truncated);
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
