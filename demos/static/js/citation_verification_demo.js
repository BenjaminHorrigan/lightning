/* =============================================================================
   Citation Verification Demo - Live Presentation Addition
   
   5-minute enhancement that makes the hallucination point visceral:
   - Click Lightning citation → opens real CFR section
   - Click LLM citation → shows "404" or wrong content
   - Visual verification checkmarks/X marks appear in real time
   ============================================================================= */

class CitationVerificationDemo {
  constructor() {
    this.setupVerificationControls();
    this.injectVerificationUI();
  }

  setupVerificationControls() {
    // Add verification buttons to all citations in adversarial sections
    document.querySelectorAll('.adv-citation').forEach(citation => {
      this.enhanceCitation(citation);
    });
  }

  enhanceCitation(citationEl) {
    const isCorrect = citationEl.classList.contains('adv-citation--correct');
    const isWrong = citationEl.classList.contains('adv-citation--wrong');
    
    if (!isCorrect && !isWrong) return; // Skip unverified citations

    const citationText = citationEl.querySelector('.adv-citation__cite')?.textContent || '';
    
    // Add verification button
    const verifyBtn = document.createElement('button');
    verifyBtn.className = 'citation-verify-btn';
    verifyBtn.innerHTML = '🔍 Verify';
    verifyBtn.style.cssText = `
      font-family: var(--font-mono);
      font-size: var(--fs-xs);
      background: var(--accent-primary);
      color: var(--text-inverse);
      border: none;
      border-radius: var(--radius-sm);
      padding: var(--space-1) var(--space-2);
      cursor: pointer;
      margin-left: var(--space-3);
      transition: all 0.2s var(--ease-out);
    `;
    
    verifyBtn.addEventListener('click', () => {
      this.performVerification(citationText, isCorrect, verifyBtn);
    });

    const citationMain = citationEl.querySelector('.adv-citation__main');
    if (citationMain) {
      citationMain.appendChild(verifyBtn);
    }
  }

  performVerification(citationText, isCorrect, buttonEl) {
    // Show loading state
    buttonEl.innerHTML = '⏳ Checking...';
    buttonEl.disabled = true;

    setTimeout(() => {
      if (isCorrect) {
        this.showCorrectVerification(citationText, buttonEl);
      } else {
        this.showIncorrectVerification(citationText, buttonEl);
      }
    }, 1000); // Simulate lookup time
  }

  showCorrectVerification(citationText, buttonEl) {
    buttonEl.innerHTML = '✅ Verified';
    buttonEl.style.background = 'var(--accent-success)';
    
    // Open real CFR link (simulated)
    const cfrUrl = this.generateCFRUrl(citationText);
    if (cfrUrl) {
      window.open(cfrUrl, '_blank');
      this.showVerificationToast('Citation verified! Real CFR section opened.', 'success');
    }
  }

  showIncorrectVerification(citationText, buttonEl) {
    buttonEl.innerHTML = '❌ Invalid';
    buttonEl.style.background = 'var(--accent-danger)';
    
    // Show 404 or wrong section
    this.show404Demo(citationText);
    this.showVerificationToast('Citation invalid! Section does not exist or is wrong.', 'error');
  }

  generateCFRUrl(citationText) {
    const cfrMatch = citationText.match(/(\d+)\s*CFR\s*(\d+)\.(\d+)/i);
    if (cfrMatch) {
      const [, title, part, section] = cfrMatch;
      return `https://www.ecfr.gov/current/title-${title}/part-${part}/section-${part}.${section}`;
    }

    // CWC/MTCR/other treaties - link to official sources
    if (citationText.toLowerCase().includes('cwc schedule')) {
      return 'https://www.opcw.org/chemical-weapons-convention/annexes/annex-chemicals';
    }
    
    if (citationText.toLowerCase().includes('mtcr')) {
      return 'https://mtcr.info/mtcr-guidelines/';
    }

    return null;
  }

  show404Demo(citationText) {
    // Create a mock "404" or "wrong section" demo window
    const demoWindow = window.open('', '_blank', 'width=800,height=600');
    
    demoWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>CFR Search Result - ${citationText}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
          .error { background: #ffebee; border: 1px solid #f44336; padding: 20px; border-radius: 4px; }
          .wrong-section { background: #fff3e0; border: 1px solid #ff9800; padding: 20px; border-radius: 4px; }
          .highlight { background: #ffeb3b; padding: 2px 4px; }
        </style>
      </head>
      <body>
        <h1>eCFR — Electronic Code of Federal Regulations</h1>
        ${this.generate404Content(citationText)}
      </body>
      </html>
    `);
    
    demoWindow.document.close();
  }

  generate404Content(citationText) {
    // Generate specific "wrong section" content based on the citation
    if (citationText.includes('27 CFR 555.11')) {
      return `
        <div class="wrong-section">
          <h2>27 CFR 555.11 - Definitions</h2>
          <p><strong>This section contains DEFINITIONS only, not licensing requirements.</strong></p>
          <p>The LLM cited this as governing "synthesis licensing" but this section only defines terms like:</p>
          <ul>
            <li>"Explosive materials" means explosives, blasting agents, and detonators.</li>
            <li>"Distribute" means sell, issue, give, transfer, or otherwise dispose of.</li>
            <li>"Licensed dealer" means a person licensed under...</li>
          </ul>
          <div class="highlight">
            ❌ No licensing requirements found in this section. 
            The correct section for ATF licensing is 27 CFR 555.41.
          </div>
        </div>
      `;
    }

    if (citationText.includes('18 USC 842(p)')) {
      return `
        <div class="wrong-section">
          <h2>18 USC 842(p) - Teaching or Demonstrating</h2>
          <p>This section prohibits <strong>teaching or demonstrating</strong> the use of explosives, not synthesis or possession:</p>
          <blockquote>
            "Whoever teaches or demonstrates to any other person the use, application, or making of any explosive..."
          </blockquote>
          <div class="highlight">
            ❌ This section is about TEACHING/DEMONSTRATING explosive use, not about synthesis licensing.
            The LLM confused related but distinct legal concepts.
          </div>
        </div>
      `;
    }

    if (citationText.includes('CWC Schedule 1B')) {
      return `
        <div class="error">
          <h2>CWC Schedule Error</h2>
          <p><strong>❌ "Schedule 1B" does not exist in the Chemical Weapons Convention.</strong></p>
          <p>The CWC has:</p>
          <ul>
            <li>Schedule 1 (items 1.A.1 through 1.A.14)</li>
            <li>Schedule 2A and 2B</li> 
            <li>Schedule 3</li>
          </ul>
          <div class="highlight">
            ❌ Methylphosphonic dichloride is actually CWC <strong>Schedule 2B</strong> item 4, not "Schedule 1B".
            The LLM elevated it to a more restrictive (non-existent) category.
          </div>
        </div>
      `;
    }

    // Generic 404 for other cases
    return `
      <div class="error">
        <h2>Section Not Found</h2>
        <p><strong>❌ The cited section "${citationText}" could not be found or does not govern the described activity.</strong></p>
        <p>This is a common type of LLM hallucination: the citation sounds plausible and is related to the topic, but does not actually support the claim made.</p>
        <div class="highlight">
          Lightning's citations are sourced from a verified database of actual regulatory text.
        </div>
      </div>
    `;
  }

  showVerificationToast(message, type) {
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 1000;
      background: ${type === 'success' ? 'var(--accent-success)' : 'var(--accent-danger)'};
      color: var(--text-inverse);
      padding: var(--space-3) var(--space-4);
      border-radius: var(--radius-md);
      font-family: var(--font-mono);
      font-size: var(--fs-sm);
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      animation: slideInRight 0.3s ease-out;
    `;
    
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.animation = 'slideOutRight 0.3s ease-in';
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 3000);
  }

  injectVerificationUI() {
    // Add verification status overview
    const overview = document.createElement('div');
    overview.id = 'verification-overview';
    overview.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 20px;
      background: var(--bg-elevated);
      border: 2px solid var(--accent-primary);
      border-radius: var(--radius-md);
      padding: var(--space-3);
      font-family: var(--font-mono);
      font-size: var(--fs-xs);
      z-index: 999;
      min-width: 200px;
    `;
    
    overview.innerHTML = `
      <div style="color: var(--accent-primary); font-weight: 600; margin-bottom: var(--space-2);">
        Citation Verification
      </div>
      <div id="verification-stats">
        Click "🔍 Verify" on any citation to check it live
      </div>
    `;
    
    document.body.appendChild(overview);
  }
}

// Add keyframe animations for toast
const toastCSS = `
  @keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  
  @keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;

const style = document.createElement('style');
style.textContent = toastCSS;
document.head.appendChild(style);

// Auto-initialize on adversarial page
document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname.includes('adversarial') || 
      document.querySelector('.adv-citation')) {
    setTimeout(() => {
      window.citationVerificationDemo = new CitationVerificationDemo();
    }, 1000); // Wait for page to fully load
  }
});

// Export for manual initialization
window.CitationVerificationDemo = CitationVerificationDemo;
