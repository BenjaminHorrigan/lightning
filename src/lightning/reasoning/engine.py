"""
Symbolic reasoning engine.

This is the beating heart of LIGHTNING. It takes a TechnicalArtifact, asserts it
as a set of facts, runs the clingo solver against the knowledge base, and
returns a ProofTree.

Design decisions:
- Answer Set Programming (ASP) via `clingo` rather than Prolog. ASP has better
  Python bindings, cleaner semantics for non-monotonic reasoning (which matters
  for the "specially designed" release paragraphs), and a more forgiving
  learning curve for someone new to logic programming.
- We load all KB modules at once, not just the "primary" regime. This means
  stubs contribute their facts too — a single artifact can be classified
  across regimes.
- Proof extraction uses clingo's justification feature (--verbose) when
  available, falling back to derived-atom enumeration otherwise.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from lightning.models import (
    CrossRegimeLink,
    ProofStep,
    ProofTree,
    Regime,
    RegulationCitation,
    TechnicalArtifact,
)


# Map regime → subdirectory under rules/. Each subdirectory may hold any
# number of .lp files; the engine loads them all when the regime is requested.
REGIME_DIRS = {
    Regime.USML: "usml",
    Regime.CWC: "cwc",
    Regime.MTCR: "mtcr",
    Regime.SELECT_AGENT: "bwc_select_agents",
    Regime.DEA: "dea",
}

RULES_DIR = Path(__file__).parent / "rules"
KB_DIR = Path(__file__).parent.parent / "knowledge_base"  # citations.json lives here

# Strip #include directives from concatenated rule text. The engine handles
# load order (always _common first), so the directives are redundant and
# clingo can't resolve their relative paths anyway when programs are added
# as text rather than loaded from disk.
_INCLUDE_RE = re.compile(r'^\s*#include\s+"[^"]*"\s*\.\s*$', re.MULTILINE)


def artifact_to_facts(artifact: TechnicalArtifact) -> list[str]:
    """
    Convert a TechnicalArtifact into a list of ASP facts that clingo can reason over.

    This is the adapter between the neural and symbolic worlds. Every fact
    emitted here becomes a premise that rules in the KB can fire on.
    """
    facts = []

    # Substances — name is canonicalized (lowercase, underscore) so extractor
    # outputs like "Hydrazine" match KB atoms like controlled_propellant("hydrazine").
    for sub in artifact.substances:
        name = _canonicalize(sub.name)
        facts.append(f'substance("{name}").')
        if sub.cas_number:
            facts.append(f'cas_number("{name}", "{_sanitize(sub.cas_number)}").')
        if sub.smiles:
            facts.append(f'smiles("{name}", "{_sanitize(sub.smiles)}").')
        if sub.role != "unknown":
            facts.append(f'substance_role("{name}", "{sub.role}").')
        # Emit quantity_mg/2 and quantity_grams/2 when unit is convertible.
        # Select-Agent toxin thresholds and CWC Schedule-2 thresholds both
        # need integer quantities on the symbolic side.
        if sub.quantity is not None and sub.quantity_unit:
            mg, g = _to_mg_and_grams(sub.quantity, sub.quantity_unit)
            if mg is not None:
                facts.append(f'quantity_mg("{name}", {mg}).')
            if g is not None:
                facts.append(f'quantity_grams("{name}", {g}).')

    # Components — display name stays as-is, category canonicalized for KB match
    for comp in artifact.components:
        name = _sanitize(comp.name)
        comp_category = _canonicalize(comp.category) if comp.category else None

        facts.append(f'component("{name}").')
        if comp_category:
            facts.append(f'component_category("{name}", "{comp_category}").')

        # If the component's category is itself an end-item type (rocket, missile,
        # uav, etc.), the component IS a system — emit system/1 and system_type/2
        # so IV(a)(2) / MTCR threshold rules can match on it without requiring a
        # separate parent_system wrapper.
        if comp_category and _is_system_category(comp_category):
            facts.append(f'system("{name}").')
            facts.append(f'system_type("{name}", "{_system_type_for(comp_category)}").')

        if comp.parent_system:
            parent = _sanitize(comp.parent_system)
            facts.append(f'parent_system("{name}", "{parent}").')
            facts.append(f'system("{parent}").')
            facts.append(f'system_type("{parent}", "{_infer_system_type(parent)}").')
            # Propagate performance specs to the parent system too. Component-
            # level parameters (shaft_speed_rpm) are no-ops at system level;
            # system-level parameters (range_km, payload_kg) now fire threshold
            # rules. Per lightning_RULE_EXPANSION.md B.2.
            for spec in comp.specifications:
                facts.append(
                    f'performance("{parent}", "{_canonicalize(spec.parameter)}", '
                    f'{int(round(spec.value))}).'
                )
        for material in comp.materials:
            facts.append(f'material("{name}", "{_sanitize(material)}").')
        for attr in comp.attributes:
            # Provenance flags driving release-paragraph reasoning.
            facts.append(f'attribute("{name}", "{_canonicalize(attr)}").')
        for spec in comp.specifications:
            # Clingo's integer sort is the only numeric type; floats like "24.0"
            # fail the parser. Round to int for threshold comparisons (rpm,
            # pressures, range_km, payload_kg — all integer-domain in practice).
            facts.append(
                f'performance("{name}", "{_canonicalize(spec.parameter)}", '
                f'{int(round(spec.value))}).'
            )

    # Procedures — substance refs canonicalized to match substance() atoms
    for step in artifact.procedures:
        facts.append(f'step({step.step_number}, "{_canonicalize(step.action)}").')
        for sub_name in step.substances:
            facts.append(f'step_uses({step.step_number}, "{_canonicalize(sub_name)}").')

    # Stated intent (string atom, rules can match on keywords)
    if artifact.stated_intent:
        facts.append(f'stated_intent("{_sanitize(artifact.stated_intent[:200])}").')

    return facts


def _sanitize(s: str) -> str:
    """Escape strings for safe embedding in ASP atoms."""
    return s.replace('"', '\\"').replace("\n", " ").strip()


def _canonicalize(s: str) -> str:
    """
    Normalize a name to the ASP-atom convention used by the KB: lowercase,
    spaces/hyphens/parenthesized-suffixes collapsed to underscores. So the
    extractor can output "Hydrazine (N2H4)" or "liquid rocket engine" and
    still match KB atoms like hydrazine and liquid_rocket_engine.
    """
    import re
    s = _sanitize(s).lower()
    # Drop any parenthesized qualifier: "hydrazine (anhydrous)" -> "hydrazine"
    s = re.sub(r"\s*\([^)]*\)", "", s)
    # Collapse non-alnum runs to a single underscore
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s


def _infer_system_type(parent_name: str) -> str:
    """Heuristic parent-system → category-IV type. Refine in production."""
    name = parent_name.lower()
    if "rocket" in name or "launch vehicle" in name or "slv" in name:
        return "rocket"
    if "missile" in name:
        return "ballistic_missile"
    if "engine" in name and any(x in name for x in ["rocket", "solid", "liquid"]):
        return "rocket"
    if "uav" in name or "drone" in name:
        return "uav"
    return "unknown"


# Categories that mean "the component is itself a top-level system".
# When a Component's .category matches one of these, we emit system/1 and
# system_type/2 facts in addition to component/1 — so threshold rules
# (IV(a)(2), MTCR Cat I) can match on standalone submissions without
# requiring a separate parent_system wrapper.
_SYSTEM_CATEGORIES = {
    "rocket", "space_launch_vehicle", "slv", "ballistic_missile",
    "cruise_missile", "sounding_rocket", "uav", "drone", "missile",
}


def _is_system_category(category: str) -> bool:
    return category in _SYSTEM_CATEGORIES


def _system_type_for(category: str) -> str:
    """Normalize a category used as a system to a system_type atom."""
    if category in ("rocket", "space_launch_vehicle", "slv", "sounding_rocket"):
        return "rocket"
    if category in ("ballistic_missile", "cruise_missile", "missile"):
        return category if category != "missile" else "ballistic_missile"
    if category in ("uav", "drone"):
        return "uav"
    return category


# Unit conversion table for Substance.quantity → (mg, grams) integers.
# Only units we can confidently map land here; others skip silently.
_UNIT_MG_PER_UNIT = {
    "mg": 1,
    "milligram": 1,
    "milligrams": 1,
    "g": 1_000,
    "gram": 1_000,
    "grams": 1_000,
    "kg": 1_000_000,
    "kilogram": 1_000_000,
    "kilograms": 1_000_000,
    "ug": 0.001,
    "microgram": 0.001,
    "micrograms": 0.001,
    "ng": 0.000_001,
}


def _to_mg_and_grams(quantity: float, unit: str) -> tuple[int | None, int | None]:
    """
    Convert (quantity, unit) into integer milligrams and grams.

    Returns (None, None) if the unit is not mass-convertible (volumes don't
    project onto a generic mass without density). Values below one unit
    round to zero, which is the safe behavior for clingo thresholds.
    """
    u = unit.strip().lower().rstrip(".")
    scale = _UNIT_MG_PER_UNIT.get(u)
    if scale is None:
        return None, None
    mg = int(round(quantity * scale))
    g = int(round(quantity * scale / 1_000))
    return mg, g


def run_reasoner(
    artifact: TechnicalArtifact,
    regimes: Optional[list[Regime]] = None,
) -> ProofTree:
    """
    Run the symbolic reasoning engine against an artifact.

    Returns a ProofTree with all derived classifications, along with gaps
    (premises the reasoner needed but could not confirm).
    """
    try:
        import clingo
    except ImportError:
        raise RuntimeError(
            "clingo not installed. Run: uv add clingo  "
            "(or pip install clingo)"
        )

    if regimes is None:
        regimes = [Regime.USML, Regime.CWC, Regime.MTCR, Regime.SELECT_AGENT]

    facts = artifact_to_facts(artifact)

    # Build the clingo program: facts + _common rules + all selected regimes
    program_parts = ["% ---- Facts from TechnicalArtifact ----"]
    program_parts.extend(facts)

    def _append_rule_file(path: Path, label: str) -> None:
        text = _INCLUDE_RE.sub("", path.read_text())
        program_parts.append(f"\n% === {label} ({path.name}) ===")
        program_parts.append(text)

    # Cross-regime doctrines (atom_vocabulary, specially_designed) load first
    common_dir = RULES_DIR / "_common"
    if common_dir.exists():
        program_parts.append("\n% ---- Common (cross-regime) ----")
        for lp in sorted(common_dir.glob("*.lp")):
            _append_rule_file(lp, "common")

    # Regime-specific rule files
    program_parts.append("\n% ---- Regime modules ----")
    for regime in regimes:
        regime_dir = RULES_DIR / REGIME_DIRS.get(regime, "")
        if not regime_dir.exists():
            continue
        for lp in sorted(regime_dir.glob("*.lp")):
            _append_rule_file(lp, regime.value)

    full_program = "\n".join(program_parts)

    # Solve
    ctl = clingo.Control(["--warn=none"])
    ctl.add("base", [], full_program)
    ctl.ground([("base", [])])

    # atoms=True (not shown=True) gives the full stable model — every ground
    # atom derived or asserted. We need that to reconstruct premise chains,
    # because the #show directives in the KB only surface the final atoms.
    derived_atoms = []
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            derived_atoms = [str(atom) for atom in model.symbols(atoms=True)]
            break  # first model is enough for decisive classifications

    return _atoms_to_proof_tree(derived_atoms, artifact)


def _atoms_to_proof_tree(
    derived_atoms: list[str],
    artifact: TechnicalArtifact,
) -> ProofTree:
    """
    Reconstruct a rule-firing proof chain from the stable model.

    The strategy is *structural*, not meta-programming: we know which KB
    rule produced each classified/N atom by inspecting the intermediate
    atoms in the model (specially_designed/1, usml_controlled_end_item/1,
    controlled_propellant/1). For each classification we emit a sequence
    of ProofSteps that mirrors the actual rule-chain in the KB — not a
    flat enumeration of everything mentioning the element.
    """
    # Index atoms by predicate so premise lookups are direct.
    by_pred = _index_atoms(derived_atoms)
    citations_table = _load_citations()

    steps: list[ProofStep] = []
    controlled_elements: list[str] = []
    top_level: str | None = None

    for atom in derived_atoms:
        if not atom.startswith("classified("):
            continue

        args = _parse_atom_args(atom)
        # Support both signatures:
        #   classified/3 — (Element, Category, CitationKey)        [legacy]
        #   classified/4 — (Element, Regime, Category, Reasoning)  [phase0 vocab]
        if len(args) == 3:
            element, classification, citation_key = args
        elif len(args) == 4:
            element, regime, category, reasoning = args
            classification = f"{regime.upper()}_{category}"
            citation_key = reasoning
        else:
            continue

        controlled_elements.append(element)
        if top_level is None:
            top_level = classification

        citation = citations_table.get(citation_key) or RegulationCitation(
            regime=_regime_for_classification(classification),
            category=classification,
            text=citation_key,
        )

        steps.extend(
            _build_rule_chain(element, classification, citation, by_pred)
        )

    # Record defeaters — release paragraphs that fired (120.41(b)(1)-(5))
    for atom in by_pred.get("released_from_control", []):
        comp = _parse_atom_args(atom)
        if comp:
            steps.append(
                ProofStep(
                    rule_name="release_from_control_120_41_b",
                    premises=[atom],
                    conclusion=(
                        f"{comp[0]} is released from 'specially designed' control "
                        f"via 22 CFR 120.41(b). Classification suppressed."
                    ),
                )
            )

    gaps = _identify_gaps(artifact, derived_atoms)
    cross_regime_links = _find_cross_regime_connections(derived_atoms)

    return ProofTree(
        steps=steps,
        controlled_elements=controlled_elements,
        top_level_classification=top_level,
        gaps=gaps,
        cross_regime_links=cross_regime_links,
    )


def _index_atoms(atoms: list[str]) -> dict[str, list[str]]:
    """Group atoms by predicate name (e.g., 'classified' -> [atom strings])."""
    out: dict[str, list[str]] = {}
    for a in atoms:
        if "(" in a:
            pred = a[: a.index("(")]
            out.setdefault(pred, []).append(a)
    return out


def _regime_for_classification(classification: str) -> Regime:
    """Map a classification code back to its originating regime."""
    if classification.startswith("USML_"):
        return Regime.USML
    if classification.startswith("CWC_"):
        return Regime.CWC
    if classification.startswith("MTCR_"):
        return Regime.MTCR
    if classification.startswith("SELECT_"):
        return Regime.SELECT_AGENT
    return Regime.USML


def _build_rule_chain(
    element: str,
    classification: str,
    citation: RegulationCitation,
    by_pred: dict[str, list[str]],
) -> list[ProofStep]:
    """
    Produce a list of ProofSteps that shows how the KB rules fired to
    derive `classified(element, classification, ...)`. Each USML rule has
    a different chain — we mirror the KB's structure.
    """
    # --- Propellant: direct substance match via controlled_propellant/1 ---
    if classification == "USML_IV_h_propellant":
        premises = [
            f'substance("{element}") — asserted from extracted artifact',
            f'controlled_propellant("{element}") — KB: enumerated propellant under 22 CFR 121.1 IV(h)(1)',
        ]
        return [
            ProofStep(
                rule_name="controlled_propellant_match",
                premises=premises,
                conclusion=f"{element} is a controlled propellant under USML_IV_h_propellant",
                citations=[citation],
            )
        ]

    # --- IV(a): directly enumerated end item ---
    if classification.startswith("USML_IV_a"):
        cat = _category_of(element, by_pred)
        premises = [
            f'component("{element}") — asserted from extracted artifact',
            f'component_category("{element}", "{cat}") — asserted from extracted artifact' if cat else '(no category facts found)',
            f'category_iv_a("{cat}") — KB: enumerated Category IV(a) end item' if cat else '',
        ]
        return [
            ProofStep(
                rule_name="direct_category_iv_a",
                premises=[p for p in premises if p],
                conclusion=f"{element} is directly enumerated under USML Category IV(a)",
                citations=[citation],
            )
        ]

    # --- IV(d): directly enumerated major component ---
    if classification.startswith("USML_IV_d"):
        cat = _category_of(element, by_pred)
        premises = [
            f'component("{element}") — asserted from extracted artifact',
            f'component_category("{element}", "{cat}") — asserted from extracted artifact' if cat else '',
            f'category_iv_d_component("{cat}") — KB: enumerated Category IV(d) component' if cat else '',
        ]
        return [
            ProofStep(
                rule_name="direct_category_iv_d",
                premises=[p for p in premises if p],
                conclusion=f"{element} is directly enumerated under USML Category IV(d)",
                citations=[citation],
            )
        ]

    # --- IV(h) via "specially designed" inheritance ---
    # This is the load-bearing multi-step chain. Emit three ProofSteps:
    #   1. system Y is a USML-controlled end item (via IV(a) category match)
    #   2. element X is specially designed for system Y
    #   3. element X's category falls under IV(h); X is therefore controlled
    if classification.startswith("USML_IV_h"):
        cat = _category_of(element, by_pred)
        parent = _parent_of(element, by_pred)
        parent_type = _system_type_of(parent, by_pred) if parent else None

        chain: list[ProofStep] = []

        if parent and parent_type:
            chain.append(
                ProofStep(
                    rule_name="usml_controlled_end_item_via_iv_a",
                    premises=[
                        f'system("{parent}") — asserted from parent_system/2',
                        f'system_type("{parent}", "{parent_type}") — inferred from parent name',
                        f'category_iv_a("{parent_type}") — KB: {parent_type} is a USML Category IV(a) end item',
                    ],
                    conclusion=f'{parent} is a USML-controlled end item',
                )
            )
            chain.append(
                ProofStep(
                    rule_name="specially_designed_via_parent_inheritance",
                    premises=[
                        f'component("{element}") — asserted from extracted artifact',
                        f'parent_system("{element}", "{parent}") — asserted from extracted artifact',
                        f'usml_controlled_end_item("{parent}") — derived in prior step',
                        'not released_from_control(...) — no 120.41(b) defeater fired',
                    ],
                    conclusion=f'{element} is specially designed under 22 CFR 120.41(b)',
                )
            )

        chain.append(
            ProofStep(
                rule_name="parts_components_accessories_iv_h",
                premises=[
                    f'component("{element}") — asserted from extracted artifact',
                    (f'component_category("{element}", "{cat}") — asserted from extracted artifact'
                     if cat else f'component_category("{element}", ?) — no category found'),
                    (f'category_iv_h_component("{cat}") — KB: enumerated IV(h) part/component'
                     if cat else ''),
                    f'specially_designed("{element}") — derived in prior step' if parent else '',
                ],
                conclusion=f'{element} is controlled under USML Category IV(h)',
                citations=[citation],
            )
        )

        # Strip empty premises from the final step for clean display
        chain[-1] = ProofStep(
            rule_name=chain[-1].rule_name,
            premises=[p for p in chain[-1].premises if p],
            conclusion=chain[-1].conclusion,
            citations=chain[-1].citations,
        )
        return chain

    # --- Fallback for other regimes (MTCR, CWC, SELECT_AGENT stubs) ---
    return [
        ProofStep(
            rule_name=_rule_name_from_classification(classification),
            premises=[a for a in by_pred.get("classified", []) if element in a],
            conclusion=f'{element} is controlled under {classification}',
            citations=[citation],
        )
    ]


def _category_of(element: str, by_pred: dict[str, list[str]]) -> str | None:
    for atom in by_pred.get("component_category", []):
        args = _parse_atom_args(atom)
        if len(args) == 2 and args[0] == element:
            return args[1]
    return None


def _parent_of(element: str, by_pred: dict[str, list[str]]) -> str | None:
    for atom in by_pred.get("parent_system", []):
        args = _parse_atom_args(atom)
        if len(args) == 2 and args[0] == element:
            return args[1]
    return None


def _system_type_of(system: str, by_pred: dict[str, list[str]]) -> str | None:
    for atom in by_pred.get("system_type", []):
        args = _parse_atom_args(atom)
        if len(args) == 2 and args[0] == system:
            return args[1]
    return None


def _parse_atom_args(atom: str) -> list[str]:
    """classified("turbopump_X", "USML_IV_h", "22 CFR ...") → list of 3 strings."""
    try:
        inside = atom[atom.index("(") + 1 : atom.rindex(")")]
        parts = []
        current = ""
        in_string = False
        depth = 0
        for char in inside:
            if char == '"' and depth == 0:
                in_string = not in_string
                continue
            if not in_string and char == "," and depth == 0:
                parts.append(current.strip())
                current = ""
            else:
                current += char
        if current:
            parts.append(current.strip())
        return parts
    except (ValueError, IndexError):
        return []


def _rule_name_from_classification(classification: str) -> str:
    """Map a classification code to the rule that produced it (for display)."""
    if classification.startswith("USML_IV_a"):
        return "direct_category_iv_a"
    if classification.startswith("USML_IV_d"):
        return "direct_category_iv_d"
    if classification == "USML_IV_h_propellant":
        return "controlled_propellant_match"
    if classification.startswith("USML_IV_h"):
        return "specially_designed_inheritance"
    return classification.lower()


def _identify_gaps(
    artifact: TechnicalArtifact,
    derived_atoms: list[str],
) -> list[str]:
    """
    Identify what the reasoner needed but couldn't confirm.

    If an artifact has components without parent_system information, the
    specially_designed rule can't fire — that's a gap that drives ESCALATE.
    """
    gaps = []

    # Collect the set of elements a 120.41(b) release fired on, so we can
    # suppress the "no parent system" gap for them — if a release already
    # established non-control, the absence of a parent system isn't a gap.
    released = set()
    for atom in derived_atoms:
        if atom.startswith("released_from_control("):
            parts = _parse_atom_args(atom)
            if parts:
                released.add(parts[0])

    for comp in artifact.components:
        if comp.category and not comp.parent_system:
            # If a release attribute is present or a release atom fired for
            # this component, the reasoner has enough to decide → no gap.
            name_canon = _sanitize(comp.name)
            if name_canon in released:
                continue
            gaps.append(
                f"Component '{comp.name}' has category '{comp.category}' but no "
                f"parent system specified. Cannot evaluate 'specially designed' "
                f"inheritance (22 CFR 120.41). Human review required to "
                f"determine intended end use."
            )

    # Stated vs inferred intent divergence — the extractor only populates
    # inferred_intent when it sees evidence of misalignment with stated_intent.
    # Any populated inferred_intent is therefore itself a signal.
    if artifact.inferred_intent and artifact.stated_intent:
        gaps.append(
            f"Stated intent (\"{artifact.stated_intent[:120]}...\") diverges "
            f"from inferred intent (\"{artifact.inferred_intent[:120]}...\"). "
            f"End-use cannot be conclusively established; human review required "
            f"to determine whether the work falls under dual-use controls."
        )

    if artifact.extraction_confidence < 0.6:
        gaps.append(
            f"Extraction confidence is {artifact.extraction_confidence:.2f}. "
            f"Some input content could not be reliably parsed. Classification "
            f"based on partial artifact representation."
        )

    return gaps


def _load_citations() -> dict[str, RegulationCitation]:
    """
    Load the citations lookup table. Maps the citation keys embedded in KB
    rules to full RegulationCitation objects with text and URLs.
    """
    citations_path = KB_DIR / "citations.json"
    if not citations_path.exists():
        return {}

    with open(citations_path) as f:
        data = json.load(f)

    return {
        key: RegulationCitation(**value) for key, value in data.items()
    }


def _find_cross_regime_connections(derived_atoms: list[str]) -> list[CrossRegimeLink]:
    """Find atoms that link classifications across regimes."""
    connections = []

    # Helper function to parse atom arguments
    def _parse_atom_args(atom):
        try:
            start = atom.index("(") + 1
            end = atom.rindex(")")
            args_str = atom[start:end]
            # Simple parsing - split by commas, strip quotes
            args = [arg.strip(' "') for arg in args_str.split(",")]
            return args
        except (ValueError, IndexError):
            return []

    # Look for MTCR markings on USML-controlled items
    for atom in derived_atoms:
        if atom.startswith("mtcr_controlled(") or "mtcr" in atom.lower():
            args = _parse_atom_args(atom)
            element = args[0] if args else ""

            # Find corresponding USML classifications
            usml_classifications = [
                a for a in derived_atoms
                if a.startswith("classified(") and element in a and "USML" in a
            ]

            if usml_classifications and element:
                connections.append(CrossRegimeLink(
                    link_type="USML_MTCR_overlap",
                    element=element,
                    regimes=["USML", "MTCR"],
                    explanation=f"{element} is controlled under both USML IV and MTCR Annex"
                ))

    # Look for substances that hit multiple regimes
    substance_regimes = {}
    for atom in derived_atoms:
        if atom.startswith("classified("):
            args = _parse_atom_args(atom)
            if len(args) >= 2:
                element, classification = args[0], args[1]
                if element not in substance_regimes:
                    substance_regimes[element] = []

                # Extract regime from classification
                if "USML" in classification:
                    substance_regimes[element].append("USML")
                elif "CWC" in classification:
                    substance_regimes[element].append("CWC")
                elif "MTCR" in classification:
                    substance_regimes[element].append("MTCR")
                elif "SELECT" in classification:
                    substance_regimes[element].append("SELECT_AGENT")

    for element, regimes in substance_regimes.items():
        if len(set(regimes)) > 1:
            connections.append(CrossRegimeLink(
                link_type="multi_regime_substance",
                element=element,
                regimes=list(set(regimes)),
                explanation=f"{element} triggers controls under {', '.join(set(regimes))}"
            ))

    # Look for parent system inheritance across regimes
    for atom in derived_atoms:
        if "parent_system" in atom and "specially_designed" in derived_atoms:
            args = _parse_atom_args(atom)
            if len(args) >= 2:
                component, system = args[0], args[1]

                # Check if this creates cross-regime implications
                system_regimes = []
                for check_atom in derived_atoms:
                    if system in check_atom and "classified(" in check_atom:
                        check_args = _parse_atom_args(check_atom)
                        if len(check_args) >= 2:
                            classification = check_args[1]
                            if "USML" in classification:
                                system_regimes.append("USML")
                            elif "MTCR" in classification:
                                system_regimes.append("MTCR")

                if len(set(system_regimes)) > 1:
                    connections.append(CrossRegimeLink(
                        link_type="parent_system_inheritance",
                        element=component,
                        regimes=list(set(system_regimes)),
                        explanation=f"{component} inherits control status from {system} across multiple regimes"
                    ))

    return connections
