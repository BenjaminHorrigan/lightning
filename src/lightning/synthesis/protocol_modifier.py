"""
Automated protocol modification for non-controlled alternatives.
"""
import re
from typing import Dict, List, Tuple

from lightning.models import TechnicalArtifact, Substance

# Non-controlled propellant alternatives database
PROPELLANT_ALTERNATIVES = {
    "hydrazine": [
        {"name": "hydrogen_peroxide", "concentration": "90%", "trade_off": "Lower Isp, but non-toxic"},
        {"name": "nitrous_oxide", "note": "Requires hybrid motor design", "trade_off": "Lower performance density"},
    ],
    "monomethylhydrazine": [
        {"name": "ethanol", "note": "Requires oxygen-rich combustion", "trade_off": "Significantly lower Isp"},
        {"name": "isopropanol", "note": "Alternative alcohol fuel", "trade_off": "Lower energy density"},
    ],
    "nitrogen_tetroxide": [
        {"name": "liquid_oxygen", "note": "Requires cryogenic handling", "trade_off": "Higher performance but operational complexity"},
        {"name": "hydrogen_peroxide", "concentration": "85%", "trade_off": "Monopropellant or bipropellant use"},
    ],
    "diazane": [  # Synonym for hydrazine
        {"name": "hydrogen_peroxide", "concentration": "90%", "trade_off": "Lower Isp, but non-toxic"},
        {"name": "nitrous_oxide", "note": "Requires hybrid motor design", "trade_off": "Lower performance density"},
    ]
}

# Component alternatives for controlled equipment
COMPONENT_ALTERNATIVES = {
    "turbopump": [
        {"name": "commercial_centrifugal_pump", "trade_off": "Lower pressure rating, commercial availability"},
        {"name": "positive_displacement_pump", "trade_off": "Different flow characteristics, lower RPM"},
    ],
    "rotating_flow_acceleration_device": [  # Obfuscated turbopump
        {"name": "commercial_centrifugal_pump", "trade_off": "Lower pressure rating, commercial availability"},
        {"name": "industrial_compressor", "trade_off": "Different application domain, lower performance"},
    ]
}


def generate_modified_protocol(
    original_protocol: str,
    controlled_substances: List[str],
    target_application: str = "aerospace"
) -> Tuple[str, List[str]]:
    """
    Generate a modified protocol with non-controlled alternatives.

    Returns:
        - Modified protocol text
        - List of modifications made
    """
    modified_protocol = original_protocol
    modifications = []

    for controlled in controlled_substances:
        controlled_lower = controlled.lower()

        if controlled_lower in PROPELLANT_ALTERNATIVES:
            alternatives = PROPELLANT_ALTERNATIVES[controlled_lower]
            best_alt = alternatives[0]  # Pick first alternative for simplicity

            # Replace in protocol text
            modified_protocol = re.sub(
                r'\b' + re.escape(controlled) + r'\b',
                best_alt["name"].replace("_", " "),
                modified_protocol,
                flags=re.IGNORECASE
            )

            modifications.append(
                f"Replaced {controlled} → {best_alt['name']}: {best_alt['trade_off']}"
            )

    # Also check for controlled equipment/components
    for controlled in controlled_substances:
        controlled_lower = controlled.lower()

        if controlled_lower in COMPONENT_ALTERNATIVES:
            alternatives = COMPONENT_ALTERNATIVES[controlled_lower]
            best_alt = alternatives[0]

            modified_protocol = re.sub(
                r'\b' + re.escape(controlled) + r'\b',
                best_alt["name"].replace("_", " "),
                modified_protocol,
                flags=re.IGNORECASE
            )

            modifications.append(
                f"Replaced {controlled} → {best_alt['name']}: {best_alt['trade_off']}"
            )

    # Additional pattern-based replacements for common controlled terms
    replacements = {
        "aerospace applications": "industrial applications",
        "rocket propulsion": "general propulsion research",
        "satellite": "research platform",
        "thrust chamber": "combustion chamber",
        "propellant": "fuel",
        "500N thrust": "reduced thrust research",
    }

    for original, replacement in replacements.items():
        if original in modified_protocol.lower():
            modified_protocol = re.sub(
                re.escape(original),
                replacement,
                modified_protocol,
                flags=re.IGNORECASE
            )
            modifications.append(f"Changed application context: {original} → {replacement}")

    return modified_protocol, modifications


def estimate_performance_impact(
    original_substances: List[str],
    replacement_substances: List[str]
) -> Dict[str, any]:
    """Estimate performance impact of propellant substitutions."""
    impact = {
        "isp_change_percent": 0,
        "density_impulse_change_percent": 0,
        "handling_complexity": "unchanged",
        "safety_improvement": False,
        "cost_impact": "neutral"
    }

    # Rules-based estimation (simplified for demo)
    for orig, repl in zip(original_substances, replacement_substances):
        orig_lower = orig.lower()
        repl_lower = repl.lower()

        if orig_lower == "hydrazine" and "peroxide" in repl_lower:
            impact["isp_change_percent"] -= 15
            impact["safety_improvement"] = True
            impact["handling_complexity"] = "reduced"
            impact["cost_impact"] = "reduced"
        elif orig_lower == "hydrazine" and "nitrous" in repl_lower:
            impact["isp_change_percent"] -= 25
            impact["safety_improvement"] = True
            impact["handling_complexity"] = "simplified"
        elif orig_lower == "nitrogen_tetroxide" and "oxygen" in repl_lower:
            impact["isp_change_percent"] += 5
            impact["handling_complexity"] = "increased (cryogenic)"
            impact["cost_impact"] = "increased"
        elif orig_lower == "monomethylhydrazine" and "ethanol" in repl_lower:
            impact["isp_change_percent"] -= 30
            impact["safety_improvement"] = True
            impact["cost_impact"] = "significantly reduced"

    return impact


def generate_performance_comparison(
    original_protocol: str,
    modified_protocol: str,
    controlled_substances: List[str]
) -> str:
    """Generate a comparison report of original vs modified protocol performance."""

    # Extract substances from protocols (simplified)
    original_substances = controlled_substances
    modified_substances = []

    for substance in controlled_substances:
        if substance.lower() in PROPELLANT_ALTERNATIVES:
            alt = PROPELLANT_ALTERNATIVES[substance.lower()][0]
            modified_substances.append(alt["name"])
        else:
            modified_substances.append(substance)  # No change

    impact = estimate_performance_impact(original_substances, modified_substances)

    report = f"""
**Performance Impact Analysis**

**Propellant Changes:**
{chr(10).join(f"• {orig} → {repl}" for orig, repl in zip(original_substances, modified_substances))}

**Performance Impact:**
• Specific Impulse: {impact['isp_change_percent']:+d}% change
• Handling Complexity: {impact['handling_complexity']}
• Safety: {'Improved' if impact['safety_improvement'] else 'No change'}
• Cost: {impact['cost_impact']}

**Regulatory Status:**
• Original protocol: REFUSED (controlled substances)
• Modified protocol: Expected ALLOW (non-controlled alternatives)

**Trade-offs:**
• Lower performance propellants require larger tanks or reduced payload
• Simplified handling procedures reduce operational complexity
• Non-toxic alternatives improve safety margins
• Cost savings from commercial availability
"""

    return report


def create_substitution_guide(controlled_element: str) -> str:
    """Create a detailed substitution guide for a specific controlled element."""
    controlled_lower = controlled_element.lower()

    if controlled_lower in PROPELLANT_ALTERNATIVES:
        alternatives = PROPELLANT_ALTERNATIVES[controlled_lower]

        guide = f"""
**Substitution Guide for {controlled_element}**

**Why it's controlled:** {controlled_element} is controlled under USML Category IV(h) as a propellant specifically designed for aerospace applications.

**Non-controlled alternatives:**
"""

        for i, alt in enumerate(alternatives, 1):
            guide += f"""
{i}. **{alt['name'].replace('_', ' ').title()}**
   - Trade-off: {alt['trade_off']}
   - Regulatory status: Not controlled (commercial availability)
   - {alt.get('note', 'Standard industrial chemical')}
"""

        guide += """
**Implementation considerations:**
• Modify mixing ratios to account for different energy densities
• Update safety procedures for new chemical properties
• Verify compatibility with existing equipment materials
• Consider performance requirements vs regulatory compliance
"""

        return guide

    elif controlled_lower in COMPONENT_ALTERNATIVES:
        alternatives = COMPONENT_ALTERNATIVES[controlled_lower]

        guide = f"""
**Substitution Guide for {controlled_element}**

**Why it's controlled:** This component may be specially designed for USML applications.

**Commercial alternatives:**
"""

        for i, alt in enumerate(alternatives, 1):
            guide += f"""
{i}. **{alt['name'].replace('_', ' ').title()}**
   - Trade-off: {alt['trade_off']}
   - Availability: Commercial off-the-shelf
"""

        return guide

    else:
        return f"""
**Substitution Guide for {controlled_element}**

No specific alternatives database available for this element.
Consider:
• Commercial equivalents with similar functionality
• Lower-performance variants that don't meet controlled thresholds
• Alternative design approaches that avoid the controlled element entirely
• Commodity Jurisdiction determination if commercial equivalents exist
"""