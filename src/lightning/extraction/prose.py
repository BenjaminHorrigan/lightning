"""
Natural-language proposal extractor.

STUB IMPLEMENTATION — supports the architectural claim that LIGHTNING handles
upstream research intent (not just downstream protocols).

This matters because some dual-use concerns arise at the proposal level
(intent to produce) even when the eventual protocol looks benign in isolation.
"""
from __future__ import annotations

import json
from typing import Optional

import anthropic

from lightning.const import DEFAULT_MODEL
from lightning.models import ArtifactType, TechnicalArtifact

_SCHEMA_TEXT = json.dumps(TechnicalArtifact.model_json_schema(), separators=(",", ":"))


PROPOSAL_EXTRACTION_PROMPT = """You are extracting structured research-intent data from a research proposal.

Your job is NOT to judge whether the research is permissible. Your job is to
produce a faithful structured record. A symbolic reasoning layer handles
classification.

Extract:
1. Stated research intent (one paragraph, direct quotation or close paraphrase)
2. Target substances, organisms, or systems (if named)
3. Methodology steps the proposal commits to (as ProcedureSteps, coarse-grained)
4. Inferred intent — what the proposal is actually trying to accomplish, if
   different from stated intent. Be conservative: only populate this if there
   is clear evidence of misalignment between stated and implied goals.

Populate extraction_warnings for:
- Ambiguity about specific substances/organisms
- Missing methodology detail that would affect classification
- Any language patterns suggesting the proposal may be obscuring true intent

Return only valid JSON matching the TechnicalArtifact schema.

Input:
{input}
"""


def extract_from_proposal_text(
    proposal_text: str,
    client: Optional[anthropic.Anthropic] = None,
    model: str = DEFAULT_MODEL,
) -> TechnicalArtifact:
    """Extract TechnicalArtifact from a natural-language proposal."""
    if client is None:
        from lightning._client import get_client
        client = get_client()

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=(
            "You extract structured research-intent data for a safety-reasoning system. "
            "You attend to both stated and implied goals.\n\n"
            f"Output must match this JSON schema:\n{_SCHEMA_TEXT}"
        ),
        messages=[
            {
                "role": "user",
                "content": PROPOSAL_EXTRACTION_PROMPT.format(input=proposal_text),
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
        data["artifact_type"] = ArtifactType.PROPOSAL
        data.setdefault("raw_input", proposal_text)
        return TechnicalArtifact.model_validate(data)
    except Exception as e:
        return TechnicalArtifact(
            artifact_type=ArtifactType.PROPOSAL,
            raw_input=proposal_text,
            extraction_confidence=0.0,
            extraction_warnings=[f"Proposal extraction failed: {e}"],
        )
