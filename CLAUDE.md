# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

LIGHTNING is a hackathon submission for the SCSP AI+Expo Hackathon 2026 (Cloud Laboratories track), submission window **Sat April 25, 10am → Sun April 26, 6pm Pacific**. It is a neurosymbolic safety layer that sits in front of autonomous research agents (ChemCrow, Coscientist, Virtual Lab) and returns auditable ALLOW/REFUSE/ESCALATE decisions on protocols, designs, and proposals. Full handoff context lives in `lightning_CLAUDE_CODE_PROMPT.md` and `lightning_STATUS.md` at the repo root (also mirrored in `.handoff/`). Read those before making non-trivial changes.

## Commands

The project uses `uv` (not pip/poetry). **`pyproject.toml` does not exist yet** — Phase 1 of the handoff is to create it. Until then, the package will not install. Required deps when scaffolding: `anthropic`, `clingo`, `pydantic>=2`, `streamlit`, `rdkit`, `python-dotenv`. Python 3.11+.

```bash
uv sync                                          # install (after pyproject.toml exists)
uv run python demos/fastapi_app.py              # FastAPI demo server with web UI
uv run lightning check examples/rocket_protocol.py   # CLI (cli.py + entry point not yet built)
uv run pytest tests/test_golden.py               # golden eval harness (not yet built)
uv run pytest tests/test_golden.py::test_name -x # single test
```

`ANTHROPIC_API_KEY` must be set (used by extraction + rationale/counterfactual generation). The model string `claude-opus-4-5` appears as a default in `extraction/protocol.py`, `extraction/design.py`, `extraction/prose.py`, and `decision/synthesizer.py` — `lightning_STATUS.md` flags this as needing confirmation against the current production model name; if you change it, change it in all four places.

## Architecture

Three-stage pipeline, single entry point `lightning.check()` in `src/lightning/__init__.py`:

```
Input → Extraction (neural)  → TechnicalArtifact
      → Reasoning  (symbolic) → ProofTree
      → Decision   (hybrid)   → ClassificationResult
```

**`models.py` is the contract between layers.** All three stages communicate exclusively through the Pydantic models defined there (`TechnicalArtifact`, `ProofTree`, `ClassificationResult`). Extending to new input types or regimes means adding fields here, not rewriting the pipeline.

### Core trust property — DO NOT VIOLATE

The symbolic layer never calls the LLM, and the LLM never overrides the symbolic decision. The LLM's only roles are (a) extraction of unstructured input → `TechnicalArtifact`, (b) rationale prose generation from a completed proof, (c) counterfactual prose for REFUSE decisions. **Do not introduce LLM-based classification anywhere in the decision path.** `_decide()` in `decision/synthesizer.py` is pure-symbolic and must stay that way.

### Layer details

- **Extraction (`extraction/`)** — Three extractors (`protocol.py`, `design.py`, `prose.py`) all return `TechnicalArtifact`. `__init__.py` auto-routes by heuristic (Opentrons keywords, JSON-shape, spec-sheet keywords, proposal keywords). `protocol.py` is deepest (LLM + direct Autoprotocol JSON parse). Every extractor sets `extraction_confidence ∈ [0,1]`; low confidence propagates to ESCALATE. Extractors must never silently guess — leaving fields null is correct behavior.

- **Reasoning (`reasoning/engine.py` + `knowledge_base/*.lp`)** — `artifact_to_facts()` adapts the Pydantic artifact into ASP facts (`substance/1`, `component/1`, `parent_system/2`, etc.). `run_reasoner()` loads all relevant `.lp` modules into one clingo program, solves, and converts derived `classified/3` atoms into a `ProofTree`. `_identify_gaps()` is what produces ESCALATEs (e.g., a component with a category but no `parent_system` cannot be evaluated for "specially designed" inheritance).

- **Decision (`decision/synthesizer.py`)** — Decision rule is symbolic: any `controlled_elements` → REFUSE; any `gaps` or `extraction_confidence < 0.5` → ESCALATE; otherwise ALLOW. Rationale and counterfactual are LLM-generated *post-hoc* with deterministic fallbacks if no `anthropic.Anthropic` client is provided.

- **Integration (`integrations/chemcrow.py`)** — `lightning_guard()` wraps an agent's `.run()` method or a callable, intercepts the output, runs `check()`, and raises `LightningRefusal` / `LightningEscalation` or returns the result based on mode. This is the deployment-story surface — the one-liner that goes in the pitch.

### Knowledge base

`knowledge_base/` is plain ASP (`.lp` files) plus `citations.json`. **Domain-coverage status is uneven by design:**
- `usml_cat_iv.lp` (160 lines) — **deep**: Category IV with the full "specially designed" inheritance logic from 22 CFR 120.41 plus release paragraphs. This is the load-bearing regime for the demo.
- `cwc_sched1.lp`, `mtcr.lp`, `select.lp` — **stubs**, intentionally shallow. They exist to prove the architecture is multi-regime; depth is post-hackathon work.

Citation keys embedded in ASP rules (e.g. `"22 CFR 121.1 Category IV(h)"`) are looked up in `citations.json` to produce `RegulationCitation` objects. **Citations must always be real.** Never let the LLM (or yourself) invent a CFR reference — `citations.json` is the source of truth.

When editing `usml_cat_iv.lp`: domain accuracy is partner-owned (rocket/research-lab background). If something looks wrong with the ASP encoding, **flag it rather than fixing it blindly**.

## Hard constraints

- **Do not refactor the architecture** without explicit buy-in. The scope (one deep regime + one deep input type + stubs for others) was chosen deliberately after pushback discussion.
- **Prefer simplicity over cleverness.** This repo has to stay readable through hack weekend by an ML practitioner and a domain expert who is part-time.
- Type hints everywhere. Python 3.11+ syntax (`X | None`, `list[T]`, `from __future__ import annotations`).
- New extractors and regimes plug into the pipeline by adding to `models.py` + `KB_MODULES` map in `reasoning/engine.py`. Don't bypass `TechnicalArtifact` as the inter-layer contract.
