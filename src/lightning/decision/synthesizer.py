"""
Decision synthesis layer.

Converts a ProofTree into a final ClassificationResult with:
- Decision (ALLOW/REFUSE/ESCALATE)
- Human-readable rationale (LLM-generated from proof)
- Counterfactual (what would change the decision)
- Confidence score

The decision logic is itself symbolic — we don't let the LLM decide whether
to allow or refuse. The LLM only explains decisions the symbolic layer made.
This is the core trust property of AEGIS.
"""
from __future__ import annotations

from typing import Optional

import anthropic

from lightning.const import DEFAULT_MODEL
from lightning.models import (
    ClassificationResult,
    Decision,
    ProofTree,
    Regime,
    RegulationCitation,
    TechnicalArtifact,
)


def synthesize(
    artifact: TechnicalArtifact,
    proof: ProofTree,
    regimes_checked: list[Regime],
    client: Optional[anthropic.Anthropic] = None,
    model: str = DEFAULT_MODEL,
) -> ClassificationResult:
    """
    Produce the final ClassificationResult from the artifact + proof tree.
    """
    decision = _decide(proof, artifact)
    confidence = _confidence(proof, artifact)
    primary_citations = _primary_citations(proof)
    rationale = _generate_rationale(artifact, proof, decision, client, model)
    counterfactual = (
        _generate_counterfactual(artifact, proof, client, model)
        if decision == Decision.REFUSE
        else None
    )
    escalation_reason = _format_escalation(proof) if decision == Decision.ESCALATE else None
    artifact_summary = _summarize_artifact(artifact)

    return ClassificationResult(
        decision=decision,
        proof_tree=proof,
        primary_citations=primary_citations,
        rationale=rationale,
        counterfactual=counterfactual,
        confidence=confidence,
        escalation_reason=escalation_reason,
        regimes_checked=regimes_checked,
        artifact_summary=artifact_summary,
    )


# ============================================================================
# Pure-symbolic decision logic — no LLM involvement
# ============================================================================

def _decide(proof: ProofTree, artifact: TechnicalArtifact) -> Decision:
    """
    Decision rule:
    - Any classification found → REFUSE
    - No classification, but gaps present → ESCALATE
    - No classification, no gaps → ALLOW
    - Very low extraction confidence → ESCALATE (even with no hits, we don't
      trust the absence of hits)
    """
    if proof.controlled_elements:
        return Decision.REFUSE

    if proof.gaps:
        return Decision.ESCALATE

    if artifact.extraction_confidence < 0.5:
        return Decision.ESCALATE

    return Decision.ALLOW


def _confidence(proof: ProofTree, artifact: TechnicalArtifact) -> float:
    """
    Composite confidence. For REFUSE decisions, confidence is how sure we are
    the classification is correct. For ALLOW, how sure we are there's nothing
    we missed.
    """
    extraction_conf = artifact.extraction_confidence
    gap_penalty = min(0.3, len(proof.gaps) * 0.1)

    if proof.controlled_elements:
        # REFUSE — confidence that this IS controlled
        return max(0.5, extraction_conf - gap_penalty * 0.5)

    # ALLOW or ESCALATE — confidence that nothing was missed
    return max(0.2, extraction_conf - gap_penalty)


def _primary_citations(proof: ProofTree) -> list[RegulationCitation]:
    """Dedupe and rank citations from the proof tree."""
    seen = set()
    citations = []
    for step in proof.steps:
        for cite in step.citations:
            key = (cite.regime, cite.category)
            if key not in seen:
                seen.add(key)
                citations.append(cite)
    return citations


# ============================================================================
# LLM-generated rationale — explains the proof, never decides
# ============================================================================

RATIONALE_PROMPT = """You are writing a compliance rationale for a safety-reasoning system.

A symbolic reasoning engine has already made the decision. Your job is ONLY to
explain it in 2-3 sentences of plain, accurate language. Do not hedge, do not
add caveats not present in the proof, and do not suggest the decision might be
wrong.

Decision: {decision}

Artifact summary:
{artifact_summary}

Proof tree (the actual reasoning the system performed):
{proof_summary}

Citations:
{citations}

Write the rationale now. Be specific about which element of the artifact
triggered the classification and which paragraph of which regulation applies.
Do not invent details. If the proof says "turbopump is controlled under
USML IV(h)", say that — do not hedge to "may be controlled".
"""


def _generate_rationale(
    artifact: TechnicalArtifact,
    proof: ProofTree,
    decision: Decision,
    client: Optional[anthropic.Anthropic],
    model: str,
) -> str:
    """Generate a human-readable rationale from the proof tree."""
    if not proof.steps and decision == Decision.ALLOW:
        return (
            f"No controlled elements detected across {len(proof.controlled_elements)} "
            f"checks. Artifact extraction confidence was "
            f"{artifact.extraction_confidence:.2f}."
        )

    if client is None:
        # Fallback: deterministic summary without LLM
        return _deterministic_rationale(proof, decision)

    proof_summary = "\n".join(
        f"- Rule {step.rule_name}: {step.conclusion}" for step in proof.steps[:5]
    )
    citations = "\n".join(
        f"- {c.regime.value} {c.category}: {c.text[:200]}"
        for c in _primary_citations(proof)[:3]
    )

    try:
        response = client.messages.create(
            model=model,
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": RATIONALE_PROMPT.format(
                    decision=decision.value,
                    artifact_summary=_summarize_artifact(artifact),
                    proof_summary=proof_summary or "(no rules fired)",
                    citations=citations or "(no citations)",
                ),
            }],
        )
        return response.content[0].text.strip()
    except Exception:
        return _deterministic_rationale(proof, decision)


def _deterministic_rationale(proof: ProofTree, decision: Decision) -> str:
    """LLM-free fallback."""
    if decision == Decision.REFUSE:
        elements = ", ".join(proof.controlled_elements[:3])
        return (
            f"Controlled elements detected: {elements}. "
            f"Classification: {proof.top_level_classification}. "
            f"See primary citations for regulatory basis."
        )
    if decision == Decision.ESCALATE:
        return (
            f"Symbolic reasoning could not produce a complete classification. "
            f"{len(proof.gaps)} gap(s) identified. Human reviewer required."
        )
    return "No controlled elements detected under any evaluated regime."


# ============================================================================
# Counterfactual generation — what would change the decision?
# ============================================================================

COUNTERFACTUAL_PROMPT = """A safety-reasoning system just REFUSED an artifact.

Explain in one sentence what specific change to the artifact would flip the
decision to ALLOW. Be concrete. Reference the actual rule that fired.

Artifact summary:
{artifact_summary}

Controlling rule that fired:
{rule}

Citation:
{citation}

Counterfactual (one sentence):"""


def _generate_counterfactual(
    artifact: TechnicalArtifact,
    proof: ProofTree,
    client: Optional[anthropic.Anthropic],
    model: str,
) -> Optional[str]:
    """Generate actionable modification suggestions."""
    if not proof.steps:
        return None

    primary_step = proof.steps[0]

    # Rule-specific counterfactual generation
    if "propellant" in primary_step.rule_name:
        return _generate_propellant_substitution(artifact, proof, client, model)
    elif primary_step.rule_name == "specially_designed_inheritance":
        return _generate_release_paragraph_guidance(artifact, proof, client, model)
    elif "MTCR" in primary_step.rule_name:
        return _generate_threshold_modification(artifact, proof, client, model)
    else:
        return _generate_generic_counterfactual(artifact, proof, client, model)


def _generate_propellant_substitution(artifact, proof, client, model):
    """Suggest non-controlled propellant alternatives."""
    controlled_substances = [
        sub.name for sub in artifact.substances
        if sub.name in proof.controlled_elements
    ]

    if not controlled_substances or not client:
        return "Consider non-controlled propellant alternatives such as hydrogen peroxide, ethanol, or nitrous oxide."

    PROPELLANT_SUBSTITUTION_PROMPT = """
    The following propellant was classified as ITAR-controlled: {controlled}

    Suggest 2-3 non-controlled propellant alternatives that would achieve similar performance characteristics for the stated application: {application}

    For each alternative, briefly explain:
    1. Why it's not ITAR-controlled
    2. Expected performance comparison
    3. Any trade-offs (safety, handling, performance)

    Be specific about chemical names and realistic about trade-offs.
    """

    try:
        response = client.messages.create(
            model=model,
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": PROPELLANT_SUBSTITUTION_PROMPT.format(
                    controlled=", ".join(controlled_substances),
                    application=artifact.stated_intent or "propulsive application"
                )
            }]
        )
        return f"Suggested modifications:\n\n{response.content[0].text}"
    except Exception:
        return None


def _generate_release_paragraph_guidance(artifact, proof, client, model):
    """Guidance on 120.41(b) release paragraphs."""
    return """To qualify for USML release under 22 CFR 120.41(b):

Option 1: Demonstrate equivalent form/fit/function to commercial item
- Document that this component has the same capabilities as a widely-available commercial turbopump
- Provide evidence of commercial sales not specifically for aerospace use

Option 2: Obtain Commodity Jurisdiction determination
- Submit DS-4076 to DDTC requesting non-USML classification
- Include technical specifications and intended end-use documentation

Option 3: Modify specifications below controlled performance thresholds
- Reduce performance parameters to levels achievable by commercial equipment
- Document that reduced capabilities meet mission requirements"""


def _generate_threshold_modification(artifact, proof, client, model):
    """Suggest modifications to stay under MTCR thresholds."""
    THRESHOLD_MODIFICATION_PROMPT = """
    This system was classified under MTCR due to exceeding range/payload thresholds.

    MTCR Category I threshold: ≥500 kg payload AND ≥300 km range

    Current system specs: {specs}

    Suggest specific modifications to stay under MTCR thresholds while maintaining mission capability:
    1. Payload reduction options
    2. Range limitation options
    3. Design modifications that inherently limit capability

    Be specific about numbers and realistic about mission impact.
    """

    # Extract performance specs from artifact
    specs = []
    for comp in artifact.components:
        for spec in comp.specifications:
            if spec.parameter in ["payload_kg", "range_km", "thrust_n"]:
                specs.append(f"{spec.parameter}: {spec.value} {spec.unit}")

    if not specs or not client:
        return "Modify system specifications to remain under MTCR Category I thresholds: <500 kg payload OR <300 km range."

    try:
        response = client.messages.create(
            model=model,
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": THRESHOLD_MODIFICATION_PROMPT.format(specs="; ".join(specs))
            }]
        )
        return response.content[0].text
    except Exception:
        return "Modify system specifications to remain under MTCR Category I thresholds."


def _generate_generic_counterfactual(artifact, proof, client, model):
    """Generic counterfactual generation using LLM."""
    primary_step = proof.steps[0]
    citation = primary_step.citations[0] if primary_step.citations else None

    if client is None:
        return None

    try:
        response = client.messages.create(
            model=model,
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": COUNTERFACTUAL_PROMPT.format(
                    artifact_summary=_summarize_artifact(artifact),
                    rule=f"{primary_step.rule_name}: {primary_step.conclusion}",
                    citation=citation.text if citation else "(none)",
                ),
            }],
        )
        return response.content[0].text.strip()
    except Exception:
        return None


# ============================================================================
# Helpers
# ============================================================================

def _format_escalation(proof: ProofTree) -> str:
    """Format the escalation reason for display."""
    if not proof.gaps:
        return "Escalation triggered by low extraction confidence."
    return " ".join(proof.gaps[:2])


def _summarize_artifact(artifact: TechnicalArtifact) -> str:
    """One-paragraph artifact summary for audit logs and LLM prompts."""
    parts = [f"Artifact type: {artifact.artifact_type.value}."]
    if artifact.substances:
        names = [s.name for s in artifact.substances[:5]]
        parts.append(f"Substances: {', '.join(names)}" + (
            f" (+{len(artifact.substances) - 5} more)" if len(artifact.substances) > 5 else ""
        ))
    if artifact.components:
        names = [c.name for c in artifact.components[:3]]
        parts.append(f"Components: {', '.join(names)}")
    if artifact.procedures:
        parts.append(f"{len(artifact.procedures)} procedure steps")
    if artifact.stated_intent:
        parts.append(f'Stated intent: "{artifact.stated_intent[:100]}"')
    return " ".join(parts)
