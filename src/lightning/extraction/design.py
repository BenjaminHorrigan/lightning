"""
Design artifact extractor.

STUB IMPLEMENTATION — supports the architectural claim that LIGHTNING handles
engineering designs, but deep parsing of CAD formats is out of scope for v1.

Current support:
- Text spec sheets (markdown, plain text) — LLM extraction
- Structured spec JSON — direct parse
- STEP/IGES files — NOT SUPPORTED (would require OpenCascade integration)
- PDF drawings — basic OCR + LLM pass, no geometry understanding

For the demo, we use text spec sheets. This is enough to show the system
classifying a turbopump spec against USML IV(h)(3) in the demo.
"""
from __future__ import annotations

import json
from typing import Optional

import anthropic

from lightning.const import DEFAULT_MODEL
from lightning.models import (
    ArtifactType,
    Component,
    PerformanceSpec,
    TechnicalArtifact,
)


DESIGN_EXTRACTION_PROMPT = """You are extracting structured component data from an engineering specification.

Your job is NOT to judge whether the design is controlled. Your job is to produce
a faithful structured record. A symbolic reasoning layer handles classification.

Given the input, extract:
1. Every component, subsystem, or part mentioned
2. Their category (turbopump, injector, combustion chamber, nozzle, guidance system, etc.)
3. Parent systems (what each component is part of — especially important for ITAR
   "specially designed" reasoning)
4. Numerical specifications with units
5. Materials
6. Any stated intent or end-use
7. Provenance attributes (see below) — populate only when explicitly stated

Pay particular attention to:
- Parent-system relationships. A turbopump that is "part of a rocket engine" is
  reasoned about very differently from a turbopump with commercial use.
- Performance parameters. Specific numbers (thrust, Isp, chamber pressure, flow
  rate) may cross regulatory thresholds.
- Materials. Certain alloys are themselves controlled.
- For complete systems (rockets, missiles, UAVs), extract system-level
  performance as PerformanceSpecs on the top-level component:
  * range_km  — maximum flight range in kilometers
  * payload_kg — payload mass capability in kilograms
  These drive the USML Category IV(a)(2) and MTCR Category I thresholds.

Provenance attributes — populate Component.attributes ONLY when the source
text explicitly states the condition. Do NOT infer from weak signals. Use
exactly these canonical strings:
- "hobby_rocket_nfpa_1122"                    (NFPA 1122 compliance asserted)
- "dod_funded_development"                    (DoD contract or program named)
- "general_commercial_availability"           (commercial equivalent asserted)
- "developed_for_both_usml_and_non_usml"      (dual-development history stated)
- "developed_only_non_usml"                   (commercial-only development)

If none of these are explicitly stated, leave attributes empty.

Set extraction_confidence accordingly.

Return only valid JSON matching the TechnicalArtifact schema.

Input:
{input}
"""


def extract_from_spec_text(
    spec_text: str,
    client: Optional[anthropic.Anthropic] = None,
    model: str = DEFAULT_MODEL,
) -> TechnicalArtifact:
    """Extract TechnicalArtifact from a text spec sheet."""
    if client is None:
        client = anthropic.Anthropic()

    schema = TechnicalArtifact.model_json_schema()

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=(
            "You extract structured engineering design data for a safety-reasoning system. "
            "You are careful to capture parent-system relationships accurately, because "
            "downstream classification depends on them.\n\n"
            f"Output must match this JSON schema:\n{json.dumps(schema, indent=2)}"
        ),
        messages=[
            {
                "role": "user",
                "content": DESIGN_EXTRACTION_PROMPT.format(input=spec_text),
            }
        ],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
        data["artifact_type"] = ArtifactType.DESIGN
        data.setdefault("raw_input", spec_text)
        return TechnicalArtifact.model_validate(data)
    except Exception as e:
        return TechnicalArtifact(
            artifact_type=ArtifactType.DESIGN,
            raw_input=spec_text,
            extraction_confidence=0.0,
            extraction_warnings=[f"Design extraction failed: {e}"],
        )


def extract_from_cad(cad_path: str) -> TechnicalArtifact:
    """
    STUB. Deep CAD parsing (STEP/IGES) would require OpenCascade or similar.
    For v1 we accept that this returns a low-confidence stub, which correctly
    causes downstream ESCALATE decisions.
    """
    return TechnicalArtifact(
        artifact_type=ArtifactType.DESIGN,
        raw_input=f"<CAD file: {cad_path}>",
        extraction_confidence=0.1,
        extraction_warnings=[
            "CAD geometry parsing not implemented in v1; "
            "geometric features cannot be classified. Human review required."
        ],
    )
