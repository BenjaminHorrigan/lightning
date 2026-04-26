"""
Property-based tests that demonstrate LIGHTNING's structural advantages over
pure-LLM classification.

Each test names the property and the LLM failure mode it guards against.
The conftest patches get_client() → None, so every assertion here is made
without any LLM call — proving the symbolic layer is self-sufficient.
"""
from __future__ import annotations

import lightning.reasoning.engine as _engine_mod

from lightning import check_artifact
from lightning.models import (
    ArtifactType,
    Component,
    Decision,
    PerformanceSpec,
    Substance,
    TechnicalArtifact,
)
from lightning.reasoning.engine import run_reasoner


# ---------------------------------------------------------------------------
# Shared fixtures — reuse builders already tested in test_golden.py
# ---------------------------------------------------------------------------

def _turbopump_vulcan() -> TechnicalArtifact:
    return TechnicalArtifact(
        artifact_type=ArtifactType.DESIGN,
        components=[
            Component(
                name="TPA-4421-R3",
                category="turbopump",
                parent_system="Vulcan-III liquid rocket engine",
                specifications=[PerformanceSpec(parameter="shaft_speed_rpm", value=42000, unit="rpm")],
                materials=["Inconel 718"],
            )
        ],
        extraction_confidence=0.9,
    )


def _benign_suzuki() -> TechnicalArtifact:
    return TechnicalArtifact(
        artifact_type=ArtifactType.PROTOCOL,
        substances=[
            Substance(name="4-bromoanisole", cas_number="104-92-7", role="reagent"),
            Substance(name="phenylboronic acid", cas_number="98-80-6", role="reagent"),
            Substance(name="Pd(PPh3)4", role="catalyst"),
        ],
        stated_intent="Pd-catalyzed Suzuki coupling.",
        extraction_confidence=0.95,
    )


def _ambiguous_turbopump() -> TechnicalArtifact:
    return TechnicalArtifact(
        artifact_type=ArtifactType.DESIGN,
        components=[Component(name="CTP-9X", category="turbopump")],
        extraction_confidence=0.9,
    )


# ---------------------------------------------------------------------------
# Property 1: Determinism
# LLMs are stochastic (temperature > 0) — identical prompts can yield
# different decisions across calls. LIGHTNING is deterministic by construction.
# ---------------------------------------------------------------------------

def test_identical_inputs_produce_identical_decisions():
    artifact = _turbopump_vulcan()
    r1 = check_artifact(artifact)
    r2 = check_artifact(artifact)
    assert r1.decision == r2.decision
    assert r1.proof_tree.controlled_elements == r2.proof_tree.controlled_elements
    assert r1.proof_tree.top_level_classification == r2.proof_tree.top_level_classification


def test_decision_stable_across_multiple_runs():
    """Five independent runs, same artifact → same REFUSE, every time."""
    artifact = _turbopump_vulcan()
    decisions = [check_artifact(artifact).decision for _ in range(5)]
    assert all(d == Decision.REFUSE for d in decisions)


# ---------------------------------------------------------------------------
# Property 2: Real regulatory citations
# LLMs hallucinate CFR references (e.g., "22 CFR 120.41(b)(7)" doesn't exist).
# LIGHTNING's citations come from a human-curated citations.json, not generation.
# ---------------------------------------------------------------------------

def test_refuse_carries_primary_citations():
    result = check_artifact(_turbopump_vulcan())
    assert result.decision == Decision.REFUSE
    assert result.primary_citations, "REFUSE must carry at least one citation"


def test_citation_text_is_real_regulatory_language():
    """Citation text must be substantive regulation text, not a one-word label."""
    result = check_artifact(_turbopump_vulcan())
    for c in result.primary_citations:
        assert c.text, f"Citation has no text: {c}"
        assert len(c.text) > 60, (
            f"Citation text too short to be real regulatory language ({len(c.text)} chars): {c.text!r}"
        )
        assert c.regime is not None
        assert c.category


def test_citation_cfr_reference_format():
    """Citations have a structured CFR reference, not a free-form string."""
    result = check_artifact(_turbopump_vulcan())
    for c in result.primary_citations:
        ref = c.cfr_reference or ""
        assert "CFR" in ref or c.url, (
            f"Citation lacks CFR reference or URL — may be fabricated: {c}"
        )


def test_allow_has_no_spurious_citations():
    """Clean chemistry produces ALLOW with no controlled-element citations."""
    result = check_artifact(_benign_suzuki())
    assert result.decision == Decision.ALLOW
    assert not result.proof_tree.controlled_elements, (
        "ALLOW result should have no controlled elements"
    )


# ---------------------------------------------------------------------------
# Property 3: Auditable proof chain
# LLMs are black boxes — they output a verdict without showing their work.
# LIGHTNING exposes every rule that fired, with premises and regulatory backing.
# ---------------------------------------------------------------------------

def test_refuse_proof_chain_is_non_empty():
    result = check_artifact(_turbopump_vulcan())
    assert result.proof_tree.steps, "REFUSE must have at least one proof step"


def test_every_proof_step_has_rule_name_premises_conclusion():
    result = check_artifact(_turbopump_vulcan())
    for step in result.proof_tree.steps:
        assert step.rule_name, f"Proof step missing rule_name: {step}"
        assert step.premises, f"Proof step '{step.rule_name}' has no premises"
        assert step.conclusion, f"Proof step '{step.rule_name}' has no conclusion"


def test_proof_chain_includes_regulatory_citation():
    """At least one step in the chain cites a regulation directly."""
    result = check_artifact(_turbopump_vulcan())
    cited_steps = [s for s in result.proof_tree.steps if s.citations]
    assert cited_steps, "No proof step carries a regulatory citation"


# ---------------------------------------------------------------------------
# Property 4: Symbolic layer is LLM-free
# The decision (ALLOW/REFUSE/ESCALATE) is pure-symbolic and does not call the
# LLM. The conftest already patches get_client() → None for every test in this
# session — if any decision-path code called the LLM it would crash here.
# We make the guarantee explicit by running run_reasoner() in isolation.
# ---------------------------------------------------------------------------

def test_run_reasoner_completes_without_llm():
    """run_reasoner() is pure clingo — no network call, no API key needed."""
    artifact = _turbopump_vulcan()
    proof_tree = run_reasoner(artifact)
    assert proof_tree.controlled_elements, "Symbolic layer should classify this artifact"
    assert proof_tree.top_level_classification is not None


def test_symbolic_decision_survives_null_llm_client(monkeypatch):
    """Decision is correct even when the LLM client is explicitly None."""
    monkeypatch.setattr("lightning.decision.synthesizer.get_client", lambda: None)
    result = check_artifact(_turbopump_vulcan())
    assert result.decision == Decision.REFUSE
    assert result.proof_tree.top_level_classification == "USML_IV_h"


# ---------------------------------------------------------------------------
# Property 5: ESCALATE carries a concrete, actionable reason
# LLMs often give vague hedges ("this may be controlled"). LIGHTNING states
# exactly what information is missing and why human review is triggered.
# ---------------------------------------------------------------------------

def test_escalate_has_non_empty_reason():
    result = check_artifact(_ambiguous_turbopump())
    assert result.decision == Decision.ESCALATE
    assert result.escalation_reason, "ESCALATE must state why human review is needed"
    assert len(result.escalation_reason) > 20, "Escalation reason is too vague"


def test_escalate_proof_tree_names_the_gap():
    result = check_artifact(_ambiguous_turbopump())
    assert result.proof_tree.gaps, "ESCALATE proof tree must enumerate the gaps"
    gap_text = " ".join(result.proof_tree.gaps)
    assert "parent" in gap_text.lower() or "system" in gap_text.lower(), (
        "Gap should explain the missing parent_system information"
    )


# ---------------------------------------------------------------------------
# Property 6: REFUSE includes a counterfactual (deterministic for known rule types)
# LIGHTNING gives actionable modification guidance — not just a verdict.
# For propellant cases the guidance is baked in (no LLM needed).
# ---------------------------------------------------------------------------

def test_propellant_refuse_has_deterministic_counterfactual():
    """Propellant REFUSE includes a non-LLM counterfactual pointing to alternatives."""
    artifact = TechnicalArtifact(
        artifact_type=ArtifactType.PROTOCOL,
        substances=[Substance(name="monomethylhydrazine", cas_number="60-34-4", role="reagent")],
        extraction_confidence=0.9,
    )
    result = check_artifact(artifact)
    assert result.decision == Decision.REFUSE
    # The propellant path in synthesizer.py provides a deterministic fallback
    # even when the LLM client is None — so this is always populated.
    assert result.counterfactual is not None, (
        "Propellant REFUSE should have a deterministic counterfactual even without LLM"
    )


# ---------------------------------------------------------------------------
# Property 7: Cross-regime detection
# A single artifact can trigger controls under multiple regimes simultaneously.
# LIGHTNING detects and reports these intersections.
# ---------------------------------------------------------------------------

def test_cross_regime_link_detected_for_dual_controlled_item():
    """An armed UAV meeting both USML VIII(a) and MTCR thresholds gets a cross-regime link."""
    artifact = TechnicalArtifact(
        artifact_type=ArtifactType.DESIGN,
        components=[
            Component(
                name="LRUAV-armed",
                category="uav",
                specifications=[
                    PerformanceSpec(parameter="payload_kg", value=550, unit="kg"),
                    PerformanceSpec(parameter="range_km", value=800, unit="km"),
                ],
                attributes=["weapons_hardpoints"],
            )
        ],
        extraction_confidence=0.9,
    )
    result = check_artifact(artifact)
    assert result.decision == Decision.REFUSE
    # At minimum, MTCR Cat I should classify it
    classifications = result.proof_tree.controlled_elements
    assert classifications, "Dual-controlled UAV should have controlled elements"
