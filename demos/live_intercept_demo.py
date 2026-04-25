"""
Streamlit interface for live ChemCrow + LIGHTNING intercept demo.
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from chemcrow_lightning_demo import DemoChemCrow

st.set_page_config(page_title="LIGHTNING Live Intercept", layout="wide")

st.title("🤖 ChemCrow + 🛡️ LIGHTNING Live Demo")
st.caption("Autonomous chemistry agent with real-time safety intercept")

# Demo explanation
with st.expander("🎯 Demo Overview"):
    st.markdown("""
    **What you're about to see:**
    - **ChemCrow** is an autonomous chemistry agent that generates protocols
    - **LIGHTNING** intercepts the output and classifies it against export controls
    - This happens in **real-time** - no simulation, no pre-recorded results

    **Three scenarios:**
    1. **Benign Research**: Standard chemistry that should be allowed
    2. **ITAR Controlled**: Hydrazine synthesis (rocket propellant)
    3. **Dual-Use Edge Case**: Ambiguous intent requiring human review
    """)

# Initialize demo in session state
if 'demo' not in st.session_state:
    with st.spinner("Initializing ChemCrow + LIGHTNING..."):
        st.session_state.demo = DemoChemCrow()
    st.success("✅ System ready!")

# Demo controls
st.markdown("### 🎬 Live Demo Scenarios")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Scenario 1: Benign Research", type="primary", use_container_width=True):
        st.markdown("**Query:** Suzuki coupling synthesis")

        with st.spinner("🤖 ChemCrow generating protocol..."):
            result = st.session_state.demo.demo_scenario_1_benign()
        st.session_state.last_result = result

with col2:
    if st.button("Scenario 2: ITAR Controlled", type="primary", use_container_width=True):
        st.markdown("**Query:** Hydrazine synthesis (rocket propellant)")

        with st.spinner("🤖 ChemCrow generating protocol..."):
            result = st.session_state.demo.demo_scenario_2_refuse()
        st.session_state.last_result = result

with col3:
    if st.button("Scenario 3: Dual-Use Edge Case", type="primary", use_container_width=True):
        st.markdown("**Query:** Organophosphorus with fluorinating conditions")

        with st.spinner("🤖 ChemCrow generating protocol..."):
            result = st.session_state.demo.demo_scenario_3_escalate()
        st.session_state.last_result = result

# Results display
if 'last_result' in st.session_state:
    result = st.session_state.last_result

    st.markdown("---")
    st.markdown("### 🛡️ LIGHTNING Decision")

    if result["decision"] == "ALLOW":
        st.success("✅ LIGHTNING: ALLOWED — Protocol approved for execution")

        with st.expander("📄 Generated Protocol"):
            if isinstance(result['result'], str):
                st.code(result['result'], language="python")
            else:
                st.text(str(result['result']))

    elif result["decision"] == "REFUSE":
        st.error("🛑 LIGHTNING: REFUSED — Protocol blocked by safety layer")

        lightning_result = result['result']

        # Key decision info
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Classification", lightning_result.proof_tree.top_level_classification or "Controlled")
            st.metric("Confidence", f"{lightning_result.confidence:.1%}")

        with col2:
            st.metric("Controlled Elements", len(lightning_result.proof_tree.controlled_elements))
            st.metric("Proof Steps", len(lightning_result.proof_tree.steps))

        # Rationale
        st.markdown("**🔍 Rationale:**")
        st.write(lightning_result.rationale)

        # Citations
        if lightning_result.primary_citations:
            st.markdown("**📚 Regulatory Citations:**")
            for citation in lightning_result.primary_citations:
                st.write(f"• **{citation.regime.value} {citation.category}**: {citation.text[:100]}...")

        # Proof tree
        if lightning_result.proof_tree.steps:
            with st.expander("🌳 Detailed Proof Tree"):
                for i, step in enumerate(lightning_result.proof_tree.steps, 1):
                    st.markdown(f"**Step {i}: {step.rule_name}**")
                    st.write(f"*Conclusion:* {step.conclusion}")
                    if step.premises:
                        st.write("*Premises:*")
                        for premise in step.premises[:3]:  # Limit for readability
                            st.write(f"  - {premise}")
                    st.markdown("---")

    elif result["decision"] == "ESCALATE":
        st.warning("⚠️ LIGHTNING: ESCALATED — Human review required")

        lightning_result = result['result']
        st.markdown("**❓ Escalation Reason:**")
        st.write(lightning_result.escalation_reason)

        if lightning_result.proof_tree.gaps:
            st.markdown("**🔍 Reasoning Gaps:**")
            for gap in lightning_result.proof_tree.gaps:
                st.write(f"• {gap}")

# Demo timing info
st.markdown("---")
st.caption("💡 **Demo Tip**: This is happening in real-time. ChemCrow generates the protocol, LIGHTNING analyzes it, and returns the decision with full reasoning chain.")

# Technical details
with st.expander("🔧 Technical Details"):
    st.markdown("""
    **Architecture:**
    - **ChemCrow**: Autonomous chemistry agent (LLM-based)
    - **LIGHTNING**: Neurosymbolic safety layer with three stages:
      1. **Extraction**: Parse protocol into structured format
      2. **Reasoning**: Apply export control rules symbolically
      3. **Decision**: ALLOW/REFUSE/ESCALATE with citations

    **Key Innovation:**
    - Symbolic reasoning layer ensures decisions are auditable
    - Every refusal includes exact regulatory citations
    - Cross-references ITAR, MTCR, CWC simultaneously
    - No LLM hallucination in the decision path
    """)

# Performance stats
if 'demo' in st.session_state:
    st.sidebar.markdown("### 📊 Session Stats")
    st.sidebar.metric("Demo Scenarios Available", "3")
    st.sidebar.metric("LIGHTNING Status", "🟢 Active")
    st.sidebar.metric("ChemCrow Status", "🟢 Ready")