// LIGHTNING Demo JavaScript

const examples = {
    benign: `from opentrons import protocol_api

metadata = {
    "protocolName": "Palladium-catalyzed Suzuki coupling",
    "description": "Standard organic synthesis protocol"
}

def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    reagents = protocol.load_labware("opentrons_24_tuberack_2ml", 2)
    pipette = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tips])

    bromoanisole = reagents.wells()[0]
    phenylboronic_acid = reagents.wells()[1]

    protocol.comment("Suzuki coupling reaction")
    pipette.transfer(100, bromoanisole, reagents.wells()[2])
    pipette.transfer(120, phenylboronic_acid, reagents.wells()[2])`,

    hydrazine: `from opentrons import protocol_api

metadata = {
    "protocolName": "Hydrazine synthesis",
    "description": "Synthesis of hydrazine for propulsion applications"
}

def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    reagents = protocol.load_labware("opentrons_24_tuberack_2ml", 2)
    pipette = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tips])

    ammonia = reagents.wells()[0]
    sodium_hypochlorite = reagents.wells()[1]

    protocol.comment("Hydrazine synthesis via Raschig process")
    protocol.comment("Target: aerospace propulsion applications")
    pipette.transfer(150, ammonia, reagents.wells()[2])
    pipette.transfer(100, sodium_hypochlorite, reagents.wells()[2])`,

    "cross-regime": `from opentrons import protocol_api

metadata = {
    "protocolName": "MMH/NTO propellant testing",
    "description": "Bipropellant characterization for 500N thrust chamber"
}

def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    reagents = protocol.load_labware("opentrons_24_tuberack_2ml", 2)
    test_chamber = protocol.load_labware("custom_test_chamber", 3)
    pipette = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tips])

    monomethylhydrazine = reagents.wells()[0]
    nitrogen_tetroxide = reagents.wells()[1]

    protocol.comment("Bipropellant testing for satellite propulsion")
    protocol.comment("Target: 500N thrust, 330s Isp, 8 bar chamber")
    pipette.transfer(150, monomethylhydrazine, test_chamber.wells()[0])
    pipette.transfer(250, nitrogen_tetroxide, test_chamber.wells()[0])`
};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const protocolInput = document.getElementById('protocol-input');
    const exampleSelect = document.getElementById('example-select');
    const analyzeSpinner = document.getElementById('analyze-spinner');

    // Example selection
    exampleSelect.addEventListener('change', function() {
        if (this.value && examples[this.value]) {
            protocolInput.value = examples[this.value];
        }
    });

    // Analyze button
    analyzeBtn.addEventListener('click', analyzeProtocol);

    // Store last result so generateModifiedProtocol can access it
    let lastAnalysisResult = null;
    let lastProtocolText = null;

    async function analyzeProtocol() {
        const protocolText = protocolInput.value.trim();
        if (!protocolText) {
            alert('Please enter a protocol to analyze');
            return;
        }

        // Show loading state
        analyzeSpinner.classList.remove('d-none');
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    protocol_text: protocolText,
                    enable_audit: true
                })
            });

            const result = await response.json();

            if (result.success) {
                lastAnalysisResult = result;
                lastProtocolText = protocolText;
                displayResult(result);
            } else {
                displayError('Analysis failed: ' + result.detail);
            }
        } catch (error) {
            displayError('Network error: ' + error.message);
        } finally {
            // Hide loading state
            analyzeSpinner.classList.add('d-none');
            analyzeBtn.disabled = false;
        }
    }

    function displayResult(result) {
        displayReasoning(result);
        displayDecision(result);
    }

    function displayReasoning(result) {
        const reasoningPane = document.getElementById('reasoning-pane');
        let html = `
            <div class="mb-3">
                <h6>Classification: ${result.proof_tree.top_level_classification || 'None'}</h6>
                <div class="row">
                    <div class="col-6"><small>Steps: ${result.proof_tree.steps.length}</small></div>
                    <div class="col-6"><small>Controlled: ${result.proof_tree.controlled_elements.length}</small></div>
                </div>
            </div>
        `;

        if (result.proof_tree.steps.length > 0) {
            html += '<h6>Proof Steps:</h6>';
            result.proof_tree.steps.forEach((step, i) => {
                html += `
                    <div class="card mb-2">
                        <div class="card-body p-2">
                            <small><strong>Step ${i+1}:</strong> ${step.rule_name}</small><br>
                            <small class="text-muted">→ ${step.conclusion}</small>
                        </div>
                    </div>
                `;
            });
        }

        if (result.proof_tree.cross_regime_links && result.proof_tree.cross_regime_links.length > 0) {
            html += '<h6 class="mt-3">Cross-regime Links:</h6>';
            result.proof_tree.cross_regime_links.forEach(link => {
                html += `
                    <div class="alert alert-info p-2 mb-2">
                        <small><strong>${link.regimes.join(' + ')}:</strong> ${link.explanation}</small>
                    </div>
                `;
            });
        }

        reasoningPane.innerHTML = html;
    }

    function displayDecision(result) {
        const decisionPane = document.getElementById('decision-pane');
        const decisionClass = {
            'ALLOW': 'success',
            'REFUSE': 'danger',
            'ESCALATE': 'warning'
        }[result.decision];

        let html = `
            <div class="alert alert-${decisionClass} text-center mb-3">
                <h4>${result.decision}</h4>
                <div>Confidence: ${(result.confidence * 100).toFixed(0)}%</div>
            </div>

            <h6>Rationale:</h6>
            <p class="small">${result.rationale}</p>
        `;

        if (result.counterfactual) {
            html += `
                <h6>Counterfactual:</h6>
                <div class="alert alert-info p-2">
                    <small>${result.counterfactual}</small>
                </div>
            `;

            if (result.decision === 'REFUSE' && result.proof_tree.controlled_elements.length > 0) {
                html += `
                    <button class="btn btn-sm btn-secondary mb-2" onclick="generateModifiedProtocol()">
                        Generate Modified Protocol
                    </button>
                `;
            }
        }

        if (result.escalation_reason) {
            html += `
                <h6>Escalation Reason:</h6>
                <div class="alert alert-warning p-2">
                    <small>${result.escalation_reason}</small>
                </div>
            `;
        }

        if (result.primary_citations && result.primary_citations.length > 0) {
            html += '<h6>Citations:</h6>';
            result.primary_citations.forEach(citation => {
                html += `
                    <div class="border p-2 mb-2">
                        <small><strong>${citation.regime} ${citation.category}</strong><br>
                        ${citation.text.substring(0, 200)}...</small>
                    </div>
                `;
            });
        }

        if (result.audit_id) {
            html += `
                <div class="mt-3 pt-3 border-top">
                    <small class="text-muted">Audit ID: ${result.audit_id}</small>
                </div>
            `;
        }

        decisionPane.innerHTML = html;
    }

    function displayError(message) {
        const reasoningPane = document.getElementById('reasoning-pane');
        const decisionPane = document.getElementById('decision-pane');

        reasoningPane.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        decisionPane.innerHTML = '';
    }

    // Make functions available globally
    window.generateModifiedProtocol = async function() {
        if (!lastAnalysisResult || !lastProtocolText) {
            alert('Run an analysis first.');
            return;
        }

        const decisionPane = document.getElementById('decision-pane');
        const modifyBtn = document.querySelector('[onclick="generateModifiedProtocol()"]');
        if (modifyBtn) modifyBtn.disabled = true;

        // Show loading state in decision pane
        decisionPane.insertAdjacentHTML('beforeend', `
            <div id="modify-loading" class="mt-3 text-muted small">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                Generating modified protocol...
            </div>
        `);

        try {
            const response = await fetch('/api/modify-protocol', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    original_protocol: lastProtocolText,
                    controlled_elements: lastAnalysisResult.proof_tree.controlled_elements,
                    target_application: 'aerospace'
                })
            });

            const result = await response.json();
            document.getElementById('modify-loading')?.remove();

            if (result.success) {
                const recheckClass = { ALLOW: 'success', REFUSE: 'danger', ESCALATE: 'warning' }[result.recheck_result.decision];
                decisionPane.insertAdjacentHTML('beforeend', `
                    <div class="mt-3 border-top pt-3">
                        <h6>Modified Protocol</h6>
                        <pre class="bg-light p-2 small" style="white-space:pre-wrap">${result.modified_protocol}</pre>
                        <h6>Re-check: <span class="badge bg-${recheckClass}">${result.recheck_result.decision}</span></h6>
                        <p class="small">${result.recheck_result.rationale}</p>
                        ${result.performance_analysis ? `<h6>Performance Notes:</h6><p class="small">${result.performance_analysis}</p>` : ''}
                    </div>
                `);
            } else {
                decisionPane.insertAdjacentHTML('beforeend', `
                    <div class="alert alert-danger mt-3 small">Modification failed: ${result.detail}</div>
                `);
            }
        } catch (error) {
            document.getElementById('modify-loading')?.remove();
            decisionPane.insertAdjacentHTML('beforeend', `
                <div class="alert alert-danger mt-3 small">Error: ${error.message}</div>
            `);
        } finally {
            if (modifyBtn) modifyBtn.disabled = false;
        }
    };
});

// Additional utility functions
function showSpinner(elementId) {
    document.getElementById(elementId).classList.remove('d-none');
}

function hideSpinner(elementId) {
    document.getElementById(elementId).classList.add('d-none');
}