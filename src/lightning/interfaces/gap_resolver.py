"""
Interactive gap resolution for ESCALATE decisions.
"""
from typing import Dict, List, Any
from lightning.models import TechnicalArtifact, ReasoningGap
from lightning.reasoning.engine import run_reasoner, artifact_to_facts

class InteractiveGapResolver:
    """Manages iterative gap resolution with user input."""

    def __init__(self, original_artifact: TechnicalArtifact, original_gaps: List[ReasoningGap]):
        self.original_artifact = original_artifact
        self.gaps = original_gaps.copy()
        self.user_responses = {}
        self.resolved_gaps = []

    def get_next_question(self) -> Dict[str, Any]:
        """Get the next unresolved gap question."""
        unresolved = [g for g in self.gaps if g.element not in self.resolved_gaps]
        if not unresolved:
            return None

        gap = unresolved[0]
        return {
            "gap_type": gap.gap_type,
            "element": gap.element,
            "description": gap.description,
            "impact": gap.impact,
            "resolution_question": gap.resolution_question,
            "fact_needed": gap.fact_needed
        }

    def answer_question(self, gap_element: str, user_answer: str) -> Dict[str, Any]:
        """
        Process user answer to a gap question.

        Returns updated artifact and new classification result.
        """
        self.user_responses[gap_element] = user_answer
        self.resolved_gaps.append(gap_element)

        # Create enhanced artifact with user responses
        enhanced_artifact = self._create_enhanced_artifact()

        # Re-run reasoner
        new_proof = run_reasoner(enhanced_artifact)

        return {
            "enhanced_artifact": enhanced_artifact,
            "proof_tree": new_proof,
            "remaining_gaps": [g for g in self.gaps if g.element not in self.resolved_gaps],
            "user_responses": self.user_responses.copy(),
            "resolved_count": len(self.resolved_gaps),
            "total_gaps": len(self.gaps)
        }

    def _create_enhanced_artifact(self) -> TechnicalArtifact:
        """Create new artifact incorporating user responses."""
        # Deep copy original artifact
        enhanced = self.original_artifact.model_copy(deep=True)

        # Apply user responses
        for element, response in self.user_responses.items():
            gap = next((g for g in self.gaps if g.element == element), None)
            if not gap:
                continue

            if gap.gap_type == "missing_parent_system":
                # Find component and set parent_system
                for comp in enhanced.components:
                    if comp.name == element:
                        comp.parent_system = response
                        break

            elif gap.gap_type == "ambiguous_category":
                # Update component category based on response
                for comp in enhanced.components:
                    if comp.name == element:
                        if "aerospace" in response.lower() or "propulsion" in response.lower():
                            comp.category = f"{comp.category}_aerospace_specialized"
                        else:
                            comp.category = f"{comp.category}_commercial_general"
                        break

            elif gap.gap_type == "substance_identification":
                # Add CAS number or SMILES to substance
                for sub in enhanced.substances:
                    if sub.name == element:
                        if response.count("-") == 2 and len(response.split("-")[0]) > 1:
                            sub.cas_number = response  # Looks like CAS format
                        else:
                            sub.smiles = response  # Assume SMILES
                        break

            elif gap.gap_type == "missing_performance_data":
                # Parse performance data from response
                # Expected format: "payload: 500 kg, range: 400 km"
                import re
                payload_match = re.search(r'payload[:\s]*(\d+)', response.lower())
                range_match = re.search(r'range[:\s]*(\d+)', response.lower())

                if payload_match or range_match:
                    # Find component with this parent system or create system component
                    system_comp = next(
                        (c for c in enhanced.components if c.parent_system == element),
                        None
                    )
                    if not system_comp:
                        from lightning.models import Component
                        system_comp = Component(
                            name=f"{element}_system",
                            category="system",
                            parent_system=element
                        )
                        enhanced.components.append(system_comp)

                    if payload_match:
                        from lightning.models import PerformanceSpec
                        payload_spec = PerformanceSpec(
                            parameter="payload_kg",
                            value=float(payload_match.group(1)),
                            unit="kg"
                        )
                        system_comp.specifications.append(payload_spec)

                    if range_match:
                        from lightning.models import PerformanceSpec
                        range_spec = PerformanceSpec(
                            parameter="range_km",
                            value=float(range_match.group(1)),
                            unit="km"
                        )
                        system_comp.specifications.append(range_spec)

        return enhanced

    def get_resolution_summary(self) -> Dict[str, Any]:
        """Get summary of resolution progress."""
        return {
            "total_gaps": len(self.gaps),
            "resolved_gaps": len(self.resolved_gaps),
            "remaining_gaps": len(self.gaps) - len(self.resolved_gaps),
            "progress_percent": (len(self.resolved_gaps) / len(self.gaps)) * 100 if self.gaps else 0,
            "user_responses": self.user_responses.copy()
        }

    def export_resolution_log(self) -> str:
        """Export the complete gap resolution process as a log."""
        log_lines = [
            "# AEGIS Interactive Gap Resolution Log",
            "",
            f"**Original Artifact:** {self.original_artifact.artifact_type.value}",
            f"**Total Gaps Identified:** {len(self.gaps)}",
            f"**Gaps Resolved:** {len(self.resolved_gaps)}",
            "",
            "## Resolution Details",
            ""
        ]

        for i, gap in enumerate(self.gaps, 1):
            status = "✅ RESOLVED" if gap.element in self.resolved_gaps else "⏳ PENDING"
            user_answer = self.user_responses.get(gap.element, "No response yet")

            log_lines.extend([
                f"### Gap {i}: {gap.gap_type}",
                f"**Status:** {status}",
                f"**Element:** {gap.element}",
                f"**Question:** {gap.resolution_question}",
                f"**User Response:** {user_answer}",
                f"**Impact:** {gap.impact}",
                ""
            ])

        return "\n".join(log_lines)


def create_structured_gaps(artifact: TechnicalArtifact, derived_atoms: list[str]) -> List[ReasoningGap]:
    """
    Enhanced gap identification with specific resolution queries.

    Returns list of ReasoningGap objects with resolution questions.
    """
    gaps = []

    for comp in artifact.components:
        if comp.category and not comp.parent_system:
            gap = ReasoningGap(
                gap_type="missing_parent_system",
                element=comp.name,
                description=f"Component '{comp.name}' has category '{comp.category}' but no parent system specified.",
                impact="Cannot evaluate 'specially designed' inheritance (22 CFR 120.41).",
                resolution_question=f"What is the '{comp.name}' component part of? (e.g., 'Falcon 9 rocket engine', 'commercial turbofan', 'research test stand')",
                fact_needed=f"parent_system(\"{comp.name}\", \"{{user_answer}}\")"
            )
            gaps.append(gap)

        # Check for ambiguous categories that need clarification
        if comp.category and comp.category.lower() in ["pump", "engine", "motor"]:
            gap = ReasoningGap(
                gap_type="ambiguous_category",
                element=comp.name,
                description=f"Component category '{comp.category}' is ambiguous.",
                impact="Cannot determine if this is aerospace-specific or general commercial equipment.",
                resolution_question=f"Is the '{comp.name}' specifically designed for aerospace/propulsion use, or is it general-purpose industrial equipment?",
                fact_needed=f"component_category(\"{comp.name}\", \"{{user_answer}}\")"
            )
            gaps.append(gap)

    # Check for substances without enough identification
    for sub in artifact.substances:
        if sub.name and not sub.cas_number and not sub.smiles:
            gap = ReasoningGap(
                gap_type="substance_identification",
                element=sub.name,
                description=f"Substance '{sub.name}' lacks chemical identification.",
                impact="Cannot verify against controlled substance lists.",
                resolution_question=f"What is the CAS number or SMILES structure for '{sub.name}'?",
                fact_needed=f"cas_number(\"{sub.name}\", \"{{user_answer}}\") OR smiles(\"{sub.name}\", \"{{user_answer}}\")"
            )
            gaps.append(gap)

    # Check for missing performance data when thresholds matter
    systems = set()
    for comp in artifact.components:
        if comp.parent_system:
            systems.add(comp.parent_system)

    for system in systems:
        has_payload = any("payload" in str(atom) for atom in derived_atoms if system in atom)
        has_range = any("range" in str(atom) for atom in derived_atoms if system in atom)

        if not has_payload or not has_range:
            gap = ReasoningGap(
                gap_type="missing_performance_data",
                element=system,
                description=f"System '{system}' is missing performance specifications.",
                impact="Cannot evaluate MTCR Category I threshold (≥500 kg payload AND ≥300 km range).",
                resolution_question=f"What is the payload capacity (kg) and maximum range (km) of the '{system}'?",
                fact_needed=f"performance(\"{system}\", \"payload_kg\", {{user_answer_1}}), performance(\"{system}\", \"range_km\", {{user_answer_2}})"
            )
            gaps.append(gap)

    return gaps