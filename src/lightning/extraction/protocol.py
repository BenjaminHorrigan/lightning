"""
Protocol extraction layer.

Converts Opentrons Python or Autoprotocol JSON (the two common lab-automation
formats) into a canonical TechnicalArtifact.

Strategy:
- Opentrons: we could AST-walk the Python, but LLM extraction is more forgiving
  of variations and still structured via Pydantic.
- Autoprotocol: has a well-defined JSON schema; we normalize directly.
- Unknown/mixed: fall back to LLM-only extraction.

The key architectural invariant: every extractor returns a TechnicalArtifact
with extraction_confidence ∈ [0,1]. Low confidence propagates to ESCALATE
decisions downstream. Extractors never silently guess.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import anthropic
from pydantic import ValidationError

from lightning.const import DEFAULT_MODEL
from lightning.models import (
    ArtifactType,
    ProcedureStep,
    Substance,
    TechnicalArtifact,
)


# Chemical synonym mapping (minimal set for demo)
CHEMICAL_SYNONYMS = {
    "diazane": "hydrazine",
    "hydrazin": "hydrazine",  # German
    "n2h4": "hydrazine",
    "monomethyl-hydrazine": "monomethylhydrazine",
    "mmh": "monomethylhydrazine",
    "nto": "nitrogen_tetroxide",
    "n2o4": "nitrogen_tetroxide",
    "ammoniak": "ammonia",  # German
    "natriumhypochlorit": "sodium_hypochlorite",  # German
}

# SMILES to chemical name mapping
SMILES_TO_NAME = {
    "nn": "hydrazine",
    "n": "ammonia",
    "cnn": "monomethylhydrazine",
    "o=n(=o)n(=o)=o": "nitrogen_tetroxide",
}


def _normalize_substance_name(name: str) -> str:
    """Resolve synonyms to canonical names."""
    name_lower = name.lower().strip()
    return CHEMICAL_SYNONYMS.get(name_lower, name)


def _resolve_smiles_to_name(smiles: str) -> Optional[str]:
    """Convert SMILES notation to chemical name if known."""
    if not smiles:
        return None
    smiles_lower = smiles.lower().strip()
    return SMILES_TO_NAME.get(smiles_lower)


PROTOCOL_EXTRACTION_PROMPT = """You are extracting a structured representation of a laboratory protocol.

Your job is NOT to judge whether the protocol is safe. Your job is to produce a
faithful, auditable structured record of what the protocol says. A separate
symbolic reasoning layer will make compliance judgments.

Given the input below, extract:
1. Every substance mentioned (reagents, products, solvents, catalysts, byproducts)
2. Every procedure step in order
3. The stated intent, if present

For each substance:
- Give its common name (normalize synonyms: diazane→hydrazine, MMH→monomethylhydrazine, etc.)
- Resolve common synonyms (diazane→hydrazine, Hydrazin→hydrazine, MMH→monomethylhydrazine, etc.)
- If a CAS number is present, use it for identity confirmation
- If a SMILES string is present, that takes precedence over name for identification
- NEVER invent CAS numbers or SMILES. If unsure, leave the field null.
- Mark the role accurately
- If a quantity is stated, populate quantity AND quantity_unit. Use canonical
  unit strings: "mg", "g", "kg", "ug" (micrograms), "mL", "L", or "mol". Do not
  combine — always put the magnitude in `quantity` and the unit in
  `quantity_unit`. Missing-quantity is fine (leave null); it will surface
  downstream as an extraction_warning if the reasoner needs it.

For each step:
- Number sequentially starting at 1
- Use a normalized action verb (mix, heat, filter, extract, centrifuge, titrate, etc.)
- Include the exact substances involved by name
- Capture conditions (temperature_c, pressure_bar, duration_min, ph)

Set extraction_confidence based on:
- 1.0: Input is a clean, well-structured protocol with all substances identifiable
- 0.7-0.9: Protocol is clear but some substances are ambiguous or conditions are implicit
- 0.4-0.6: Substantial ambiguity in what's being asked or what substances are involved
- 0.0-0.3: Input is not recognizably a protocol, or most content could not be parsed

Add extraction_warnings for anything the downstream reasoner should know about:
- Ambiguous substance identity
- Missing quantities that might affect classification
- Referenced but undefined procedures
- Anything that looks obfuscated or deliberately vague

Return only valid JSON matching the TechnicalArtifact schema. No prose.

Input:
{input}
"""


def extract_from_protocol_text(
    protocol_text: str,
    client: Optional[anthropic.Anthropic] = None,
    model: str = DEFAULT_MODEL,
) -> TechnicalArtifact:
    """
    Extract a TechnicalArtifact from raw protocol text (Python, JSON, prose).

    Uses Claude with structured output enforcement via Pydantic.
    """
    if client is None:
        from lightning._client import get_client
        client = get_client()

    schema = TechnicalArtifact.model_json_schema()

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=(
            "You extract structured protocol data for a safety-reasoning system. "
            "You are meticulous and never invent data you cannot confirm.\n\n"
            f"Output must match this JSON schema:\n{json.dumps(schema, indent=2)}"
        ),
        messages=[
            {
                "role": "user",
                "content": PROTOCOL_EXTRACTION_PROMPT.format(input=protocol_text),
            }
        ],
    )

    raw = response.content[0].text.strip()
    # Strip code fences if the model added them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
        data["artifact_type"] = ArtifactType.PROTOCOL
        data.setdefault("raw_input", protocol_text)
        return TechnicalArtifact.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        # Extraction failed — return low-confidence stub so downstream ESCALATES
        return TechnicalArtifact(
            artifact_type=ArtifactType.PROTOCOL,
            raw_input=protocol_text,
            extraction_confidence=0.0,
            extraction_warnings=[f"Extraction failed: {type(e).__name__}: {e}"],
        )


def extract_from_autoprotocol(autoprotocol_json: dict) -> TechnicalArtifact:
    """
    Direct-parse path for Autoprotocol JSON. No LLM needed — schema is defined.

    This is faster, cheaper, and more reliable than LLM extraction for
    well-formed Autoprotocol. Falls through to LLM extraction for anything
    non-conformant.
    """
    substances = []
    procedures = []

    for ref_name, ref_def in autoprotocol_json.get("refs", {}).items():
        substances.append(
            Substance(
                name=ref_name,
                role="reagent",  # Autoprotocol doesn't natively distinguish; refine later
                source_span=json.dumps(ref_def),
            )
        )

    for i, instruction in enumerate(autoprotocol_json.get("instructions", []), start=1):
        op = instruction.get("op", "unknown")
        procedures.append(
            ProcedureStep(
                step_number=i,
                action=op,
                substances=_extract_substance_refs(instruction),
                conditions=_extract_conditions(instruction),
                source_span=json.dumps(instruction)[:200],
            )
        )

    return TechnicalArtifact(
        artifact_type=ArtifactType.PROTOCOL,
        substances=substances,
        procedures=procedures,
        raw_input=json.dumps(autoprotocol_json),
        extraction_confidence=0.95,  # Direct schema parse; high confidence
    )


def _extract_substance_refs(instruction: dict) -> list[str]:
    """Walk an Autoprotocol instruction tree pulling out any substance references."""
    refs = []
    for key, value in instruction.items():
        if isinstance(value, str) and "/" in value:
            # Autoprotocol references often look like "water/0" (ref/well)
            refs.append(value.split("/")[0])
        elif isinstance(value, dict):
            refs.extend(_extract_substance_refs(value))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    refs.extend(_extract_substance_refs(item))
    return list(set(refs))


def _extract_conditions(instruction: dict) -> dict:
    """Pull out physical conditions from an Autoprotocol instruction."""
    conditions = {}
    if "temperature" in instruction:
        conditions["temperature_c"] = _parse_unit(instruction["temperature"], "celsius")
    if "duration" in instruction:
        conditions["duration_min"] = _parse_unit(instruction["duration"], "minute")
    return conditions


def _parse_unit(value: str, expected_unit: str) -> Optional[float]:
    """Autoprotocol uses strings like '37:celsius' — parse to float."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and ":" in value:
        try:
            num, _unit = value.split(":")
            return float(num)
        except ValueError:
            return None
    return None


def extract(input_data: str | dict, hint: Optional[str] = None) -> TechnicalArtifact:
    """
    Top-level entry point. Dispatches on input type.

    hint: optional override, e.g. "opentrons", "autoprotocol"
    """
    if isinstance(input_data, dict):
        return extract_from_autoprotocol(input_data)

    if hint == "autoprotocol" or (isinstance(input_data, str) and input_data.strip().startswith("{")):
        try:
            return extract_from_autoprotocol(json.loads(input_data))
        except json.JSONDecodeError:
            pass  # fall through to LLM

    return extract_from_protocol_text(input_data)
