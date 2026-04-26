"""
LIGHTNING core data models.

These define the canonical representations that flow through the extraction →
reasoning → decision pipeline. Extending to new input types or regimes means
adding fields here, not rewriting the pipeline.
"""
from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Input-side models (extraction layer output)
# ============================================================================

class Substance(BaseModel):
    """A chemical substance referenced in a protocol or design."""
    name: str
    cas_number: Optional[str] = None
    smiles: Optional[str] = Field(None, description="Canonical SMILES if known")
    quantity: Optional[float] = None
    quantity_unit: Optional[str] = None
    role: Literal["reagent", "product", "solvent", "catalyst", "byproduct", "unknown"] = "unknown"
    source_span: Optional[str] = Field(None, description="The text fragment this was extracted from")


class ProcedureStep(BaseModel):
    """A single action in a protocol."""
    step_number: int
    action: str = Field(description="Normalized verb: mix, heat, filter, extract, centrifuge, etc.")
    substances: list[str] = Field(default_factory=list, description="References to Substance.name")
    conditions: dict = Field(default_factory=dict, description="temperature_c, pressure_bar, duration_min, ph")
    equipment: Optional[str] = None
    source_span: Optional[str] = None


class PerformanceSpec(BaseModel):
    """Numerical performance parameter of a design."""
    parameter: str  # e.g., "specific_impulse", "max_thrust", "chamber_pressure"
    value: float
    unit: str
    conditions: Optional[str] = None  # e.g., "vacuum", "sea_level"


class Component(BaseModel):
    """An engineering component or subsystem."""
    name: str
    part_number: Optional[str] = None
    category: Optional[str] = None  # e.g., "turbopump", "injector", "combustion_chamber"
    parent_system: Optional[str] = None  # what it's part of
    specifications: list[PerformanceSpec] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    attributes: list[str] = Field(
        default_factory=list,
        description=(
            "Provenance flags that drive release-paragraph reasoning. Only "
            "populate when explicitly stated in source. Canonical values: "
            "'hobby_rocket_nfpa_1122', 'dod_funded_development', "
            "'general_commercial_availability', "
            "'developed_for_both_usml_and_non_usml', 'developed_only_non_usml'."
        ),
    )
    source_span: Optional[str] = None


class ArtifactType(str, Enum):
    PROTOCOL = "protocol"        # Opentrons Python, Autoprotocol, wet-lab procedure
    DESIGN = "design"            # CAD, engineering drawing, spec sheet
    PROPOSAL = "proposal"        # Natural-language research proposal
    MIXED = "mixed"              # Multi-modal submission


class TechnicalArtifact(BaseModel):
    """
    Canonical structured representation of whatever was submitted.

    This is the contract between the extraction (neural) layer and the
    reasoning (symbolic) layer. The symbolic layer should not need to know
    what the input modality was.
    """
    artifact_type: ArtifactType
    substances: list[Substance] = Field(default_factory=list)
    procedures: list[ProcedureStep] = Field(default_factory=list)
    components: list[Component] = Field(default_factory=list)
    stated_intent: Optional[str] = Field(
        None,
        description="Research goal or downstream use as stated by submitter"
    )
    inferred_intent: Optional[str] = Field(
        None,
        description="What the LLM believes the artifact is actually for, when stated intent is absent or suspicious"
    )
    raw_input: Optional[str] = Field(None, description="Original submission text for audit")
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    extraction_warnings: list[str] = Field(
        default_factory=list,
        description="Things the extractor is uncertain about"
    )


# ============================================================================
# Reasoning-side models (symbolic layer output)
# ============================================================================

class Regime(str, Enum):
    USML = "USML"             # ITAR - US Munitions List
    CCL = "CCL"               # EAR - Commerce Control List (ECCNs)
    CWC = "CWC"               # Chemical Weapons Convention
    AG = "AG"                 # Australia Group (biological)
    MTCR = "MTCR"             # Missile Technology Control Regime
    NRC_110 = "10CFR110"      # Nuclear (NRC import/export)
    SELECT_AGENT = "SELECT_AGENT"  # HHS/USDA Select Agents
    DEA = "DEA"               # Drug Enforcement Administration (Controlled Substances Act)


class RegulationCitation(BaseModel):
    """Points at a specific paragraph of a specific regulation."""
    regime: Regime
    category: str = Field(description="e.g., 'IV(h)(3)' for USML Category IV, paragraph h, subparagraph 3")
    text: str = Field(description="The actual regulation text at this citation")
    url: Optional[str] = None
    cfr_reference: Optional[str] = Field(None, description="e.g., '22 CFR 121.1'")


class ProofStep(BaseModel):
    """One inference step in the proof tree."""
    rule_name: str = Field(description="e.g., 'specially_designed', 'parts_components_accessories'")
    premises: list[str] = Field(description="Facts or prior conclusions that triggered this rule")
    conclusion: str
    citations: list[RegulationCitation] = Field(default_factory=list)


class CrossRegimeLink(BaseModel):
    """Relationship between classifications across regimes."""
    link_type: Literal["USML_MTCR_overlap", "multi_regime_substance", "parent_system_inheritance"]
    element: str
    regimes: list[str] = Field(default_factory=list)
    explanation: str


class ReasoningGap(BaseModel):
    """A specific reasoning gap with resolution question."""
    gap_type: Literal["missing_parent_system", "ambiguous_category", "substance_identification", "missing_performance_data"]
    element: str
    description: str
    impact: str
    resolution_question: str
    fact_needed: str


class ProofTree(BaseModel):
    """
    The full reasoning chain produced by the symbolic layer.

    A ProofTree is *auditable*: every step cites the rule that fired and the
    regulatory text backing that rule. This is the core artifact that makes
    LIGHTNING defensible in ways pure-LLM classification is not.
    """
    steps: list[ProofStep]
    controlled_elements: list[str] = Field(
        description="Which parts of the input artifact triggered control (substance names, component names, etc.)"
    )
    top_level_classification: Optional[str] = Field(
        None,
        description="e.g., 'USML IV(h)(3)' if positively classified"
    )
    gaps: list[str] = Field(
        default_factory=list,
        description="Premises the reasoner needed but could not confirm (drives ESCALATE decisions)"
    )
    cross_regime_links: list[CrossRegimeLink] = Field(
        default_factory=list,
        description="Relationships between classifications across regimes"
    )


# ============================================================================
# Decision-side models (final output)
# ============================================================================

class Decision(str, Enum):
    ALLOW = "ALLOW"
    REFUSE = "REFUSE"
    ESCALATE = "ESCALATE"


class ClassificationResult(BaseModel):
    """
    The final output of LIGHTNING. This is what gets returned to the calling
    agent / cloud lab / reviewer.
    """
    decision: Decision
    proof_tree: ProofTree
    primary_citations: list[RegulationCitation] = Field(
        description="Most load-bearing regulation references for this decision"
    )
    rationale: str = Field(
        description="Human-readable explanation generated from the proof tree"
    )
    counterfactual: Optional[str] = Field(
        None,
        description="What would need to change for the decision to flip (important for REFUSE)"
    )
    confidence: float = Field(ge=0.0, le=1.0)
    escalation_reason: Optional[str] = Field(
        None,
        description="If ESCALATE, specifically why human review is needed"
    )
    regimes_checked: list[Regime] = Field(
        description="Which regulatory regimes were evaluated"
    )
    artifact_summary: str = Field(
        description="One-paragraph summary of what was submitted, for audit logs"
    )
    audit_id: Optional[str] = Field(
        None,
        description="UUID assigned by the audit logger after a decision is persisted"
    )
