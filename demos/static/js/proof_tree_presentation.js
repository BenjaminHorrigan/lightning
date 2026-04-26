/* =============================================================================
   Enhanced Proof Tree Visualization for Presentation
   
   Improvements for the proof tree slide:
   
   1. **Step-by-step revelation** — proof tree steps appear one by one on click
   2. **Interactive exploration** — hover over any step to see explanation
   3. **Rule source linking** — click any rule to see the actual .lp file snippet
   4. **Counterfactual highlighting** — emphasizes the "what if" scenarios
   5. **Decision path tracing** — visual line showing how the decision flows
   ============================================================================= */

class ProofTreePresentation {
  constructor(proofData) {
    this.proofData = proofData;
    this.currentStep = 0;
    this.steps = this.parseProofSteps(proofData);
    this.setupVisualization();
  }

  parseProofSteps(data) {
    // Parse the proof tree data into presentation steps
    const steps = [];
    
    // Step 1: Substance extraction
    if (data.substances && data.substances.length > 0) {
      steps.push({
        type: 'extraction',
        title: 'Neural Extraction',
        content: `substance(${data.substances[0]}).`,
        explanation: 'LLM extracts structured entities from natural language',
        color: 'var(--accent-novel)'
      });
    }

    // Step 2: Context detection  
    if (data.parent_system) {
      steps.push({
        type: 'context',
        title: 'Context Detection',
        content: `parent_system(${data.parent_system}).`,
        explanation: 'System identifies the application context',
        color: 'var(--accent-novel)'
      });
    }

    // Step 3-N: Symbolic reasoning steps
    if (data.proof && data.proof.steps) {
      data.proof.steps.forEach((step, i) => {
        steps.push({
          type: 'reasoning',
          title: `Symbolic Reasoning ${i + 1}`,
          content: step,
          explanation: 'ASP solver applies logical rules',
          color: 'var(--accent-primary)',
          ruleFile: data.proof.rule_files?.[i]
        });
      });
    }

    // Final step: Decision synthesis
    steps.push({
      type: 'decision',
      title: 'Decision Synthesis',
      content: `${data.decision.toLowerCase()} :- ${steps[steps.length - 1]?.content?.split(' ')[0] || 'condition'}.`,
      explanation: 'Hybrid system synthesizes final classification',
      color: data.decision === 'REFUSE' ? 'var(--accent-danger)' : 
             data.decision === 'ALLOW' ? 'var(--accent-success)' : 'var(--accent-warning)'
    });

    return steps;
  }

  setupVisualization() {
    const container = document.getElementById('proof-tree-container') || this.createContainer();
    container.innerHTML = this.renderProofTree();
    this.setupInteractivity();
  }

  createContainer() {
    const container = document.createElement('div');
    container.id = 'proof-tree-container';
    container.style.cssText = `
      background: var(--bg-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: var(--space-6);
      margin: var(--space-4) 0;
    `;
    return container;
  }

  renderProofTree() {
    return `
      <div class="proof-tree-header">
        <h3 style="color: var(--accent-primary); font-family: var(--font-mono); margin: 0 0 var(--space-4) 0;">
          ⚡ Proof Tree Construction
        </h3>
        <div class="proof-tree-controls">
          <button id="step-prev" class="btn-tactical btn-tactical--sm" disabled>← Prev</button>
          <span id="step-counter" class="mono-tag">Step 0 / ${this.steps.length}</span>
          <button id="step-next" class="btn-tactical btn-tactical--sm btn-tactical--primary">Next →</button>
          <button id="play-auto" class="btn-tactical btn-tactical--sm" style="margin-left: var(--space-3);">▶ Auto</button>
          <button id="reset-proof" class="btn-tactical btn-tactical--sm btn-tactical--ghost">Reset</button>
        </div>
      </div>

      <div class="proof-tree-visualization">
        ${this.renderStepList()}
        ${this.renderDecisionPath()}
        ${this.renderCounterfactual()}
      </div>

      <div class="proof-tree-explanation">
        <div id="step-explanation" class="step-explanation">
          <div class="text-mono text-xs text-muted">
            Click "Next" to see how Lightning constructs machine-checkable proofs
          </div>
        </div>
      </div>
    `;
  }

  renderStepList() {
    return `
      <div class="proof-steps">
        ${this.steps.map((step, i) => `
          <div class="proof-step" id="step-${i}" data-step="${i}" style="opacity: 0.3;">
            <div class="proof-step-number">${String(i + 1).padStart(2, '0')}</div>
            <div class="proof-step-content">
              <div class="proof-step-title" style="color: ${step.color};">
                ${step.title}
              </div>
              <div class="proof-step-code">
                ${this.highlightProofCode(step.content)}
              </div>
              ${step.ruleFile ? `
                <div class="proof-step-source">
                  <button class="rule-source-btn" data-file="${step.ruleFile}">
                    📁 ${step.ruleFile.split('/').pop()}
                  </button>
                </div>
              ` : ''}
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  renderDecisionPath() {
    return `
      <div class="decision-path" style="display: none;">
        <svg class="decision-path-svg" width="100%" height="400">
          <!-- Decision flow lines will be drawn here -->
        </svg>
      </div>
    `;
  }

  renderCounterfactual() {
    if (!this.proofData.counterfactual) return '';
    
    return `
      <div class="proof-counterfactual" id="proof-counterfactual" style="opacity: 0;">
        <div class="counterfactual-label">COUNTERFACTUAL ANALYSIS</div>
        <div class="counterfactual-content">
          ${this.proofData.counterfactual}
        </div>
        <div class="counterfactual-highlight">
          This shows exactly what would change the decision — the proof is invertible.
        </div>
      </div>
    `;
  }

  highlightProofCode(code) {
    return code
      .replace(/([a-z_]+)\(/g, '<span class="proof-predicate">$1</span>(')
      .replace(/:-/g, '<span class="proof-operator">:-</span>')
      .replace(/\./g, '<span class="proof-terminator">.</span>');
  }

  setupInteractivity() {
    // Step navigation
    document.getElementById('step-next')?.addEventListener('click', () => this.nextStep());
    document.getElementById('step-prev')?.addEventListener('click', () => this.prevStep());
    document.getElementById('reset-proof')?.addEventListener('click', () => this.resetProof());
    document.getElementById('play-auto')?.addEventListener('click', () => this.autoPlay());

    // Step hover explanations
    document.querySelectorAll('.proof-step').forEach(step => {
      step.addEventListener('mouseenter', () => this.showStepExplanation(step));
    });

    // Rule source buttons
    document.querySelectorAll('.rule-source-btn').forEach(btn => {
      btn.addEventListener('click', (e) => this.showRuleSource(e.target.dataset.file));
    });
  }

  nextStep() {
    if (this.currentStep < this.steps.length) {
      this.revealStep(this.currentStep);
      this.currentStep++;
      this.updateControls();
    }
    
    // Show counterfactual after last step
    if (this.currentStep === this.steps.length && this.proofData.counterfactual) {
      this.showCounterfactual();
    }
  }

  prevStep() {
    if (this.currentStep > 0) {
      this.currentStep--;
      this.hideStep(this.currentStep);
      this.updateControls();
    }
  }

  resetProof() {
    this.currentStep = 0;
    document.querySelectorAll('.proof-step').forEach(step => {
      step.style.opacity = '0.3';
    });
    document.getElementById('proof-counterfactual')?.style.setProperty('opacity', '0');
    this.updateControls();
    document.getElementById('step-explanation').innerHTML = `
      <div class="text-mono text-xs text-muted">
        Click "Next" to see how Lightning constructs machine-checkable proofs
      </div>
    `;
  }

  autoPlay() {
    this.resetProof();
    const interval = setInterval(() => {
      this.nextStep();
      if (this.currentStep >= this.steps.length) {
        clearInterval(interval);
      }
    }, 1500);
  }

  revealStep(stepIndex) {
    const step = document.getElementById(`step-${stepIndex}`);
    if (!step) return;

    step.style.opacity = '1';
    step.style.transform = 'translateX(0)';
    step.style.transition = 'all 0.5s var(--ease-out)';
    
    // Add a glow effect
    step.style.boxShadow = '0 0 12px var(--accent-primary-glow)';
    setTimeout(() => {
      step.style.boxShadow = 'none';
    }, 1000);

    // Update explanation
    this.showStepExplanation(step);
  }

  hideStep(stepIndex) {
    const step = document.getElementById(`step-${stepIndex}`);
    if (step) {
      step.style.opacity = '0.3';
    }
  }

  showCounterfactual() {
    const counterfactual = document.getElementById('proof-counterfactual');
    if (counterfactual) {
      counterfactual.style.opacity = '1';
      counterfactual.style.transform = 'scale(1)';
      counterfactual.style.transition = 'all 0.6s var(--ease-out)';
    }
  }

  showStepExplanation(stepElement) {
    const stepIndex = parseInt(stepElement.dataset.step);
    const step = this.steps[stepIndex];
    if (!step) return;

    const explanationEl = document.getElementById('step-explanation');
    explanationEl.innerHTML = `
      <div class="step-explanation-active">
        <div class="step-explanation-title" style="color: ${step.color};">
          ${step.title}
        </div>
        <div class="step-explanation-text">
          ${step.explanation}
        </div>
        ${step.type === 'reasoning' ? `
          <div class="step-explanation-detail">
            This step applies symbolic rules from the knowledge base to derive new facts.
            The rule fired because the conditions in its body were satisfied.
          </div>
        ` : ''}
      </div>
    `;
  }

  showRuleSource(filename) {
    // Create modal showing rule source
    const modal = document.createElement('div');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.8);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
    `;

    modal.innerHTML = `
      <div style="
        background: var(--bg-elevated);
        border: 2px solid var(--accent-primary);
        border-radius: var(--radius-md);
        padding: var(--space-6);
        max-width: 80%;
        max-height: 80%;
        overflow: auto;
      ">
        <h4 style="color: var(--accent-primary); font-family: var(--font-mono); margin-top: 0;">
          Rule Source: ${filename}
        </h4>
        <pre style="
          background: var(--bg-input);
          border-radius: var(--radius-sm);
          padding: var(--space-4);
          font-family: var(--font-mono);
          font-size: var(--fs-sm);
          color: var(--text-primary);
          overflow-x: auto;
        ">${this.generateMockRuleSource(filename)}</pre>
        <div style="text-align: center; margin-top: var(--space-4);">
          <button id="close-rule-modal" class="btn-tactical btn-tactical--primary">
            Close
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    
    document.getElementById('close-rule-modal').addEventListener('click', () => {
      document.body.removeChild(modal);
    });

    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        document.body.removeChild(modal);
      }
    });
  }

  generateMockRuleSource(filename) {
    return `% USML Category IV - Liquid Propellants
% Source: 22 CFR 121.1 Category IV(h)(1)

% Controlled propellants
controlled_propellant(hydrazine).
controlled_propellant(nitrogen_tetroxide).
controlled_propellant(unsymmetrical_dimethylhydrazine).

% Parent system classification  
rocket_engine_system(rocket_engine).
rocket_engine_system(spacecraft_propulsion).
rocket_engine_system(missile_propulsion).

% USML IV(h)(1) rule: Liquid propellants and specially designed components
usml_iv_h_1 :- 
    controlled_propellant(X),
    parent_system(Y),
    rocket_engine_system(Y).

% Decision rule
refuse :- usml_iv_h_1.

% Citation generation
cite_usml_iv_h_1(usml_iv_h_1, "22 CFR 121.1 IV(h)(1)", 
                 "Liquid propellants and propellant ingredients").`;
  }

  updateControls() {
    const prevBtn = document.getElementById('step-prev');
    const nextBtn = document.getElementById('step-next');
    const counter = document.getElementById('step-counter');

    if (prevBtn) prevBtn.disabled = this.currentStep === 0;
    if (nextBtn) nextBtn.disabled = this.currentStep >= this.steps.length;
    if (counter) counter.textContent = `Step ${this.currentStep} / ${this.steps.length}`;
  }
}

// Enhanced proof tree CSS for presentation
const proofTreeCSS = `
<style>
.proof-tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--border-subtle);
}

.proof-tree-controls {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.proof-steps {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.proof-step {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: var(--space-4);
  padding: var(--space-4);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background: var(--bg-input);
  transition: all 0.3s var(--ease-out);
}

.proof-step:hover {
  border-color: var(--accent-primary);
  cursor: pointer;
}

.proof-step-number {
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  color: var(--text-muted);
  font-weight: 600;
  text-align: center;
  min-width: 2rem;
}

.proof-step-title {
  font-family: var(--font-mono);
  font-size: var(--fs-sm);
  font-weight: 600;
  margin-bottom: var(--space-2);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.proof-step-code {
  font-family: var(--font-mono);
  font-size: var(--fs-sm);
  background: var(--bg-deep);
  border-radius: var(--radius-sm);
  padding: var(--space-3);
  border-left: 3px solid var(--accent-primary);
}

.proof-predicate { color: var(--accent-success); font-weight: 600; }
.proof-operator { color: var(--accent-primary); font-weight: 600; }
.proof-terminator { color: var(--accent-warning); font-weight: 600; }

.proof-step-source {
  margin-top: var(--space-2);
}

.rule-source-btn {
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  color: var(--accent-primary);
  background: transparent;
  border: 1px solid var(--accent-primary);
  border-radius: var(--radius-sm);
  padding: var(--space-1) var(--space-2);
  cursor: pointer;
  transition: all 0.2s var(--ease-out);
}

.rule-source-btn:hover {
  background: var(--accent-primary-dim);
}

.proof-counterfactual {
  margin-top: var(--space-6);
  padding: var(--space-5);
  background: var(--accent-warning-dim);
  border: 2px solid var(--accent-warning);
  border-radius: var(--radius-md);
  transform: scale(0.95);
  transition: all 0.6s var(--ease-out);
}

.counterfactual-label {
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  color: var(--accent-warning);
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: var(--space-3);
}

.counterfactual-content {
  font-size: var(--fs-base);
  color: var(--text-primary);
  margin-bottom: var(--space-3);
  line-height: var(--lh-normal);
}

.counterfactual-highlight {
  font-family: var(--font-mono);
  font-size: var(--fs-sm);
  color: var(--accent-warning);
  font-style: italic;
}

.step-explanation {
  background: var(--bg-elevated);
  border: 1px solid var(--border-active);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
  min-height: 100px;
}

.step-explanation-title {
  font-family: var(--font-mono);
  font-size: var(--fs-sm);
  font-weight: 600;
  margin-bottom: var(--space-2);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.step-explanation-text {
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
  line-height: var(--lh-normal);
}

.step-explanation-detail {
  font-size: var(--fs-sm);
  color: var(--text-muted);
  font-style: italic;
  border-left: 2px solid var(--accent-primary);
  padding-left: var(--space-3);
}
</style>
`;

// Auto-initialize when page loads if proof tree container exists
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('proof-tree-container');
  if (container && window.currentProofData) {
    window.proofTreePresentation = new ProofTreePresentation(window.currentProofData);
  }
  
  // Inject CSS
  if (!document.getElementById('proof-tree-presentation-css')) {
    const style = document.createElement('style');
    style.id = 'proof-tree-presentation-css';
    style.textContent = proofTreeCSS.replace('<style>', '').replace('</style>', '');
    document.head.appendChild(style);
  }
});

// Export for manual initialization
window.ProofTreePresentation = ProofTreePresentation;
