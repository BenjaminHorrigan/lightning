"""
LIGHTNING top-level pipeline.

    from lightning import check
    result = check(protocol_text)

One call. Three stages. Auditable proof tree.
"""
from __future__ import annotations

from typing import Optional

# Load .env (ANTHROPIC_API_KEY, LIGHTNING_MODEL, etc.) before any submodule
# instantiates an Anthropic client. Best-effort — silently skip if dotenv
# isn't installed or there's no .env file.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from lightning.decision.synthesizer import synthesize
from lightning.extraction import design, prose, protocol
from lightning.models import (
    ArtifactType,
    ClassificationResult,
    Regime,
    TechnicalArtifact,
)
from lightning.reasoning.engine import run_reasoner


DEFAULT_REGIMES = [Regime.USML, Regime.CWC, Regime.MTCR, Regime.SELECT_AGENT]


def check(
    input_data: str | dict,
    artifact_type: Optional[ArtifactType] = None,
    regimes: Optional[list[Regime]] = None,
    hint: Optional[str] = None,
    enable_audit: bool = True,
    audit_context: Optional[dict] = None,
) -> ClassificationResult:
    """
    Run the full LIGHTNING pipeline on an input with optional audit logging.

    Args:
        input_data: raw text, JSON, or pre-parsed dict
        artifact_type: force a specific extractor; otherwise auto-detected
        regimes: which regulatory regimes to check; defaults to all
        hint: optional extractor hint (e.g. "opentrons", "autoprotocol")
        enable_audit: whether to log this decision to the audit trail
        audit_context: additional context for audit log

    Returns:
        ClassificationResult with decision, proof tree, rationale, citations.
    """
    regimes = regimes or DEFAULT_REGIMES

    # Stage 1: extraction
    artifact = _extract(input_data, artifact_type, hint)

    # Stage 2: symbolic reasoning
    proof = run_reasoner(artifact, regimes=regimes)

    # Stage 3: decision synthesis
    result = synthesize(artifact, proof, regimes_checked=regimes)

    # Stage 4: audit logging (if enabled)
    if enable_audit:
        try:
            from lightning.audit.logger import get_audit_logger
            logger = get_audit_logger()
            audit_id = logger.log_decision(artifact, result, audit_context)

            # Add audit ID to result for traceability
            result.audit_id = audit_id
        except Exception as e:
            # Don't fail the classification if audit logging fails
            print(f"Warning: Audit logging failed: {e}")

    return result


def check_artifact(
    artifact: TechnicalArtifact,
    regimes: Optional[list[Regime]] = None,
) -> ClassificationResult:
    """
    Check a pre-extracted artifact. Useful when the caller has already
    parsed the input (e.g., a cloud lab with its own protocol AST).
    """
    regimes = regimes or DEFAULT_REGIMES
    proof = run_reasoner(artifact, regimes=regimes)
    return synthesize(artifact, proof, regimes_checked=regimes)


def _extract(
    input_data: str | dict,
    artifact_type: Optional[ArtifactType],
    hint: Optional[str],
) -> TechnicalArtifact:
    """Dispatch to the right extractor."""
    if artifact_type == ArtifactType.PROTOCOL:
        return protocol.extract(input_data, hint=hint)
    if artifact_type == ArtifactType.DESIGN:
        return design.extract_from_spec_text(str(input_data))
    if artifact_type == ArtifactType.PROPOSAL:
        return prose.extract_from_proposal_text(str(input_data))

    # Auto-detect
    if isinstance(input_data, dict):
        return protocol.extract_from_autoprotocol(input_data)

    text = str(input_data).strip()

    # Heuristic routing
    if text.startswith("{") or hint == "autoprotocol":
        return protocol.extract(text, hint="autoprotocol")
    if "from opentrons" in text or "protocol.load_labware" in text:
        return protocol.extract(text, hint="opentrons")
    if any(kw in text.lower() for kw in [
        "thrust", "isp", "chamber pressure", "turbopump", "nozzle", "specific impulse"
    ]):
        return design.extract_from_spec_text(text)
    if any(kw in text.lower() for kw in [
        "proposal", "research plan", "hypothesis", "objective"
    ]):
        return prose.extract_from_proposal_text(text)

    # Default to protocol extractor
    return protocol.extract(text)
