/* =============================================================================
   Enhanced Adversarial Slide for Presentation
   
   Improvements for the adversarial → tab → proof tree flow:
   
   1. **Live tab integration** — button that opens adversarial tab in same window
      with smooth transition, then provides "Back to presentation" link
      
   2. **Proof tree preview** — small preview of what the proof tree looks like 
      before the full proof tree slide
      
   3. **Scorecard animation** — the 5/5, 2/5, 5/5 numbers animate in sequence
      to emphasize the citation accuracy gap
      
   4. **Section highlights** — when presenting, can click to highlight each
      section (epistemics, citations, determinism) individually
   ============================================================================= */

// Enhanced presentation slide functionality
class AdversarialSlideEnhancer {
  constructor() {
    this.currentHighlight = null;
    this.animationQueue = [];
    this.setupSlideControls();
  }

  setupSlideControls() {
    // Add presentation mode controls that don't interfere with normal demo
    if (window.location.search.includes('presentation=true')) {
      this.addPresentationControls();
    }
  }

  addPresentationControls() {
    const controlsHTML = `
      <div class="presentation-controls" style="
        position: fixed; 
        bottom: 20px; 
        right: 20px; 
        z-index: 1000;
        background: var(--bg-elevated);
        border: 1px solid var(--border-active);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        display: flex;
        gap: var(--space-2);
        font-family: var(--font-mono);
        font-size: var(--fs-xs);
      ">
        <button id="highlight-epistemics" class="btn-tactical btn-tactical--sm">
          Highlight Epistemics
        </button>
        <button id="highlight-citations" class="btn-tactical btn-tactical--sm">
          Highlight Citations
        </button>
        <button id="highlight-determinism" class="btn-tactical btn-tactical--sm">
          Highlight Determinism
        </button>
        <button id="animate-scorecard" class="btn-tactical btn-tactical--sm btn-tactical--primary">
          Animate Scorecard
        </button>
        <button id="show-proof-preview" class="btn-tactical btn-tactical--sm">
          Proof Preview
        </button>
        <button id="clear-highlights" class="btn-tactical btn-tactical--sm btn-tactical--ghost">
          Clear
        </button>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', controlsHTML);
    this.wireControls();
  }

  wireControls() {
    document.getElementById('highlight-epistemics')?.addEventListener('click', 
      () => this.highlightSection('section-a'));
    document.getElementById('highlight-citations')?.addEventListener('click', 
      () => this.highlightSection('section-b'));
    document.getElementById('highlight-determinism')?.addEventListener('click', 
      () => this.highlightSection('section-c'));
    document.getElementById('animate-scorecard')?.addEventListener('click', 
      () => this.animateScorecard());
    document.getElementById('show-proof-preview')?.addEventListener('click', 
      () => this.showProofPreview());
    document.getElementById('clear-highlights')?.addEventListener('click', 
      () => this.clearHighlights());
  }

  highlightSection(sectionId) {
    this.clearHighlights();
    
    const section = document.getElementById(sectionId);
    if (!section) return;

    section.style.cssText = `
      transform: scale(1.02);
      box-shadow: 0 0 20px var(--accent-primary-glow);
      border: 2px solid var(--accent-primary);
      transition: all 0.3s var(--ease-out);
      position: relative;
      z-index: 10;
    `;
    
    this.currentHighlight = section;
    
    // Scroll into view smoothly
    section.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Add a subtle pulse effect
    this.addPulseEffect(section);
  }

  addPulseEffect(element) {
    let pulseCount = 0;
    const pulse = () => {
      if (pulseCount >= 3) return;
      
      element.style.transform = 'scale(1.05)';
      setTimeout(() => {
        element.style.transform = 'scale(1.02)';
        pulseCount++;
        if (pulseCount < 3) setTimeout(pulse, 600);
      }, 200);
    };
    setTimeout(pulse, 500);
  }

  animateScorecard() {
    const agreedValue = document.getElementById('agreed-value');
    const llmCiteValue = document.getElementById('llm-cite-value');
    const lightningCiteValue = document.getElementById('lightning-cite-value');

    if (!agreedValue || !llmCiteValue || !lightningCiteValue) return;

    // Reset values
    [agreedValue, llmCiteValue, lightningCiteValue].forEach(el => {
      el.textContent = '--';
      el.style.transform = 'scale(0.8)';
      el.style.opacity = '0.3';
    });

    // Animate in sequence
    setTimeout(() => {
      agreedValue.textContent = '5/5';
      agreedValue.style.transform = 'scale(1.1)';
      agreedValue.style.opacity = '1';
      agreedValue.style.color = 'var(--accent-success)';
    }, 300);

    setTimeout(() => {
      llmCiteValue.textContent = '2/5';
      llmCiteValue.style.transform = 'scale(1.1)';
      llmCiteValue.style.opacity = '1';
      llmCiteValue.style.color = 'var(--accent-danger)';
    }, 800);

    setTimeout(() => {
      lightningCiteValue.textContent = '5/5';
      lightningCiteValue.style.transform = 'scale(1.1)';
      lightningCiteValue.style.opacity = '1';
      lightningCiteValue.style.color = 'var(--accent-success)';
    }, 1300);

    // Add emphasis effect
    setTimeout(() => {
      [llmCiteValue, lightningCiteValue].forEach(el => {
        el.style.transform = 'scale(1.2)';
        el.style.fontWeight = '800';
      });
    }, 1800);

    setTimeout(() => {
      [agreedValue, llmCiteValue, lightningCiteValue].forEach(el => {
        el.style.transform = 'scale(1)';
      });
    }, 2300);
  }

  showProofPreview() {
    const preview = document.createElement('div');
    preview.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 1000;
      background: var(--bg-elevated);
      border: 2px solid var(--accent-primary);
      border-radius: var(--radius-md);
      padding: var(--space-6);
      max-width: 600px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    `;

    preview.innerHTML = `
      <div style="margin-bottom: var(--space-4);">
        <h3 style="color: var(--accent-primary); font-family: var(--font-mono); margin: 0 0 var(--space-2) 0;">
          ⚡ Proof Tree Preview
        </h3>
        <p style="color: var(--text-secondary); font-size: var(--fs-sm); margin: 0;">
          Next: See how Lightning constructs machine-checkable proofs
        </p>
      </div>

      <div style="background: var(--bg-input); border-radius: var(--radius-sm); padding: var(--space-4); font-family: var(--font-mono); font-size: var(--fs-sm);">
        <div style="color: var(--text-muted); margin-bottom: var(--space-3);">01. Substance extraction</div>
        <div style="color: var(--accent-success); margin-bottom: var(--space-3);">
          &nbsp;&nbsp;substance(hydrazine).
        </div>
        
        <div style="color: var(--text-muted); margin-bottom: var(--space-3);">02. Parent system context</div>
        <div style="color: var(--accent-success); margin-bottom: var(--space-3);">
          &nbsp;&nbsp;parent_system(rocket_engine).
        </div>
        
        <div style="color: var(--text-muted); margin-bottom: var(--space-3);">03. Rule application</div>
        <div style="color: var(--accent-primary); margin-bottom: var(--space-3);">
          &nbsp;&nbsp;usml_iv_h_1 :- controlled_propellant(X), parent_system(rocket_engine).
        </div>
        
        <div style="color: var(--text-muted); margin-bottom: var(--space-3);">04. Decision derivation</div>
        <div style="color: var(--accent-danger); margin-bottom: var(--space-3);">
          &nbsp;&nbsp;refuse :- usml_iv_h_1.
        </div>

        <div style="color: var(--accent-warning); font-size: var(--fs-xs); margin-top: var(--space-4); padding: var(--space-3); background: var(--accent-warning-dim); border-radius: var(--radius-sm);">
          <strong>Counterfactual:</strong> Would be ALLOW if parent_system ≠ rocket_engine
        </div>
      </div>

      <div style="text-align: center; margin-top: var(--space-5);">
        <button id="close-preview" class="btn-tactical btn-tactical--primary">
          Continue to Proof Tree Slide
        </button>
      </div>
    `;

    document.body.appendChild(preview);

    // Close on click
    document.getElementById('close-preview').addEventListener('click', () => {
      document.body.removeChild(preview);
    });

    // Close on escape
    const escapeHandler = (e) => {
      if (e.key === 'Escape') {
        document.body.removeChild(preview);
        document.removeEventListener('keydown', escapeHandler);
      }
    };
    document.addEventListener('keydown', escapeHandler);
  }

  clearHighlights() {
    if (this.currentHighlight) {
      this.currentHighlight.style.cssText = '';
      this.currentHighlight = null;
    }
    
    // Clear any existing highlights
    document.querySelectorAll('.hud-panel').forEach(panel => {
      panel.style.transform = '';
      panel.style.boxShadow = '';
      panel.style.border = '';
      panel.style.zIndex = '';
    });
  }
}

// Enhanced tab integration for presentation flow
class PresentationTabManager {
  constructor() {
    this.presentationMode = window.location.search.includes('presentation=true');
    this.setupTabIntegration();
  }

  setupTabIntegration() {
    if (this.presentationMode) {
      this.addBackToPresentationButton();
      this.enhanceTabNavigation();
    }
  }

  addBackToPresentationButton() {
    // Add a "Back to Presentation" button when in presentation mode
    const backButton = document.createElement('div');
    backButton.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 1001;
    `;
    backButton.innerHTML = `
      <button id="back-to-presentation" class="btn-tactical btn-tactical--primary" style="
        padding: var(--space-3) var(--space-5);
        font-size: var(--fs-sm);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      ">
        ← Back to Presentation
      </button>
    `;
    
    document.body.appendChild(backButton);
    
    document.getElementById('back-to-presentation').addEventListener('click', () => {
      this.showTransitionMessage();
      const from = new URLSearchParams(window.location.search).get('from');
      const target = from ? `/presentation#${from}` : '/presentation';
      setTimeout(() => { window.location.href = target; }, 400);
    });
  }

  showTransitionMessage() {
    const message = document.createElement('div');
    message.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 1002;
      background: var(--accent-primary);
      color: var(--text-inverse);
      padding: var(--space-4) var(--space-6);
      border-radius: var(--radius-md);
      font-family: var(--font-mono);
      font-size: var(--fs-base);
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    `;
    message.textContent = 'Transitioning back to presentation...';
    
    document.body.appendChild(message);
    
    setTimeout(() => {
      document.body.removeChild(message);
    }, 2000);
  }

  enhanceTabNavigation() {
    // Add smooth scrolling and highlights when sections are opened
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.target.classList.contains('adv-comparison')) {
          // A comparison section was loaded, enhance it for presentation
          this.enhanceComparisonSection(mutation.target);
        }
      });
    });

    document.querySelectorAll('.adv-comparison').forEach(target => {
      observer.observe(target, { childList: true, subtree: true });
    });
  }

  enhanceComparisonSection(section) {
    // Add presentation-friendly highlights to comparison sections
    const llmSide = section.querySelector('.adv-side:not(.adv-side--lightning)');
    const lightningSide = section.querySelector('.adv-side--lightning');

    if (llmSide && lightningSide) {
      // Add subtle borders for clarity in presentation
      llmSide.style.border = '2px solid var(--accent-warning)';
      lightningSide.style.border = '2px solid var(--accent-primary)';
      
      // Add labels for presentation clarity
      this.addPresentationLabels(llmSide, lightningSide);
    }
  }

  addPresentationLabels(llmSide, lightningSide) {
    const llmLabel = document.createElement('div');
    llmLabel.style.cssText = `
      position: absolute;
      top: -8px;
      left: var(--space-3);
      background: var(--accent-warning);
      color: var(--text-inverse);
      padding: var(--space-1) var(--space-3);
      border-radius: var(--radius-sm);
      font-family: var(--font-mono);
      font-size: var(--fs-xs);
      font-weight: 600;
      letter-spacing: 1px;
      text-transform: uppercase;
    `;
    llmLabel.textContent = 'LLM Response';
    
    const lightningLabel = document.createElement('div');
    lightningLabel.style.cssText = llmLabel.style.cssText.replace('var(--accent-warning)', 'var(--accent-primary)');
    lightningLabel.textContent = 'Lightning Response';
    
    llmSide.style.position = 'relative';
    lightningSide.style.position = 'relative';
    
    llmSide.appendChild(llmLabel);
    lightningSide.appendChild(lightningLabel);
  }
}

// Auto-initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
  window.adversarialSlideEnhancer = new AdversarialSlideEnhancer();
  window.presentationTabManager = new PresentationTabManager();
  
  console.log('Presentation enhancements loaded');
});

// Export for manual control if needed
window.AdversarialSlideEnhancer = AdversarialSlideEnhancer;
window.PresentationTabManager = PresentationTabManager;
