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

# Pre-computed once at import time — schema is constant, no need to rebuild per call.
# Compact separators shave ~40% off the JSON size vs. indent=2.
_SCHEMA_TEXT = json.dumps(TechnicalArtifact.model_json_schema(), separators=(",", ":"))


# Chemical synonym mapping — covers IUPAC names, German, abbreviations, and common obfuscations.
# Applied deterministically after LLM extraction so the KB always sees canonical names.
CHEMICAL_SYNONYMS: dict[str, str] = {
    # Hydrazine variants
    "diazane": "hydrazine",           # IUPAC systematic name
    "hydrazin": "hydrazine",          # German
    "hydrazine anhydrous": "hydrazine",
    "hydrazine monohydrate": "hydrazine",
    "n2h4": "hydrazine",
    "diamine": "hydrazine",
    # MMH variants
    "monomethyl-hydrazine": "monomethylhydrazine",
    "mmh": "monomethylhydrazine",
    "1-methylhydrazine": "monomethylhydrazine",
    "methylhydrazine": "monomethylhydrazine",
    # UDMH variants
    "udmh": "unsymmetrical_dimethylhydrazine",
    "1,1-dimethylhydrazine": "unsymmetrical_dimethylhydrazine",
    "dimethylhydrazine": "unsymmetrical_dimethylhydrazine",
    "asymmetrical dimethylhydrazine": "unsymmetrical_dimethylhydrazine",
    # NTO variants
    "nto": "nitrogen_tetroxide",
    "n2o4": "nitrogen_tetroxide",
    "dinitrogen tetroxide": "nitrogen_tetroxide",
    "nitrogen(iv) oxide": "nitrogen_tetroxide",
    "stickstofftetroxid": "nitrogen_tetroxide",  # German
    # German names for common reagents in Raschig synthesis
    "ammoniak": "ammonia",
    "natriumhypochlorit": "sodium_hypochlorite",
    "calciumhypochlorit": "calcium_hypochlorite",
    # Perchlorate variants
    "ap": "ammonium_perchlorate",
    "ammonium perchlorate": "ammonium_perchlorate",
    # Explosives / energetics
    "hmx": "hmx",
    "octogen": "hmx",
    "cyclotetramethylenetetranitramine": "hmx",
    "rdx": "rdx",
    "hexogen": "rdx",
    "cyclonite": "rdx",
    "cl-20": "cl_20",
    "cl20": "cl_20",
    "hniw": "cl_20",
    "hexanitrohexaazaisowurtzitane": "cl_20",
    "cagliostro": "cl_20",
    # Sarin / nerve agents
    "gb": "sarin",
    "isopropyl methylphosphonofluoridate": "sarin",
    "vx": "vx",
    "o-ethyl s-[2-(diisopropylamino)ethyl] methylphosphonothioate": "vx",
    # Phosgene
    "carbonyl chloride": "phosgene",
    "dichloroformaldehyde": "phosgene",
}

# SMILES → canonical name. Applied case-insensitively after extraction.
SMILES_TO_NAME: dict[str, str] = {
    "nn": "hydrazine",
    "n-n": "hydrazine",
    "[nh2][nh2]": "hydrazine",
    "n": "ammonia",
    "[nh3]": "ammonia",
    "cnn": "monomethylhydrazine",
    "cn-n": "monomethylhydrazine",
    "o=n(=o)n(=o)=o": "nitrogen_tetroxide",
    "o=n+([o-])on+(=o)=o": "nitrogen_tetroxide",
    "clc(=o)cl": "phosgene",
    "fp(=o)(oc(c)c)oc(c)c": "sarin",
}

# CAS registry number → canonical name. Highest-confidence override: CAS numbers are unambiguous.
CAS_TO_NAME: dict[str, str] = {
    "302-01-2":     "hydrazine",
    "60-34-4":      "monomethylhydrazine",
    "57-14-7":      "unsymmetrical_dimethylhydrazine",
    "10544-72-6":   "nitrogen_tetroxide",
    "7616-94-6":    "ammonium_perchlorate",
    "2691-41-0":    "hmx",
    "121-82-4":     "rdx",
    "135285-90-4":  "cl_20",
    "75-44-5":      "phosgene",
    "107-44-8":     "sarin",
    "50782-69-9":   "vx",
    "7664-41-7":    "ammonia",
    "7681-52-9":    "sodium_hypochlorite",
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


def _normalize_substances(artifact: TechnicalArtifact) -> TechnicalArtifact:
    """
    Deterministic post-extraction normalization pass.

    Applies synonym → canonical name, CAS-number override, and SMILES resolution
    to every substance in the artifact. This runs AFTER the LLM extraction so
    that adversarial obfuscations (synonym substitution, foreign-language names,
    SMILES-only encoding) are caught regardless of whether the LLM normalized them.

    Priority: CAS number (unambiguous) > SMILES lookup > synonym table.
    """
    if not artifact.substances:
        return artifact

    normalized = []
    changed = False
    for sub in artifact.substances:
        name = sub.name

        # Synonym table (IUPAC, German, abbreviations)
        canonical = _normalize_substance_name(name)

        # CAS override — highest confidence: CAS 302-01-2 is always hydrazine
        if sub.cas_number:
            cas_key = sub.cas_number.strip()
            cas_canonical = CAS_TO_NAME.get(cas_key)
            if cas_canonical:
                canonical = cas_canonical

        # SMILES resolution — secondary fallback when synonym lookup didn't help
        if sub.smiles and canonical == name:
            smiles_canonical = _resolve_smiles_to_name(sub.smiles)
            if smiles_canonical:
                canonical = smiles_canonical

        if canonical != name:
            sub = sub.model_copy(update={"name": canonical})
            changed = True
        normalized.append(sub)

    return artifact.model_copy(update={"substances": normalized}) if changed else artifact


PROTOCOL_EXTRACTION_PROMPT = """You are extracting a structured representation of a laboratory protocol.

Your job is NOT to judge whether the protocol is safe. Your job is to produce a
faithful, auditable structured record of what the protocol says. A separate
symbolic reasoning layer will make compliance judgments.

Given the input below, extract:
1. Every substance mentioned (reagents, products, solvents, catalysts, byproducts)
2. Every procedure step in order
3. The stated intent, if present
4. Any equipment or devices described — even when named circumlocutionally. Identify
   the actual engineering function: "rotating flow acceleration device for propulsion"
   → component category "turbopump"; "high-pressure fluid delivery system" → "pump";
   "energetic compound for propulsion" → extract as a substance with propellant role.
   Include the parent system when stated (e.g., "for a 500 kN propulsion assembly" →
   parent_system: "propulsion assembly").

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

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=(
            "You extract structured protocol data for a safety-reasoning system. "
            "You are meticulous and never invent data you cannot confirm.\n\n"
            f"Output must match this JSON schema:\n{_SCHEMA_TEXT}"
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
        artifact = TechnicalArtifact.model_validate(data)
        return _normalize_substances(artifact)
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
