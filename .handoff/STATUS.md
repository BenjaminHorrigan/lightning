# AEGIS — Build Status

**As of handoff to Claude Code.** 2,287 lines of code and KB across 17 files.

## Architecture recap

```
Input (protocol / design / proposal)
        │
        ▼
   Extraction (neural, LLM → Pydantic)
        │
        ▼
   Reasoning (symbolic, clingo/ASP → ProofTree)
        │
        ▼
   Decision (hybrid, proof → ALLOW/REFUSE/ESCALATE + rationale)
```

---

## Status by component

### ✅ Complete and coherent

| File | LoC | Status |
|---|---|---|
| `src/aegis/models.py` | 185 | ✅ Full Pydantic data model, no known gaps |
| `src/aegis/__init__.py` | 106 | ✅ Top-level `check()` entry point with auto-routing |
| `src/aegis/extraction/protocol.py` | 226 | ✅ Opentrons + Autoprotocol extraction, LLM + direct-parse |
| `src/aegis/extraction/design.py` | 124 | ✅ Text spec extractor (primary), CAD stub |
| `src/aegis/extraction/prose.py` | 91 | ✅ Proposal extractor |
| `src/aegis/reasoning/engine.py` | 303 | ✅ Clingo wrapper, facts injection, gap detection |
| `src/aegis/decision/synthesizer.py` | 311 | ✅ Decision logic, LLM rationale, counterfactual |
| `src/aegis/integrations/chemcrow.py` | 164 | ✅ `aegis_guard()` decorator + Refusal/Escalation exceptions |
| `src/aegis/knowledge_base/usml_cat_iv.lp` | 160 | ✅ **Deep**: Category IV with specially-designed inheritance, release paragraphs, propellants |
| `src/aegis/knowledge_base/citations.json` | 51 | ✅ Citation lookup with real CFR references |
| `src/aegis/knowledge_base/cwc_sched1.lp` | 54 | ✅ **Stub**: named Schedule 1 + OP+F heuristic |
| `src/aegis/knowledge_base/mtcr.lp` | 19 | ✅ **Stub**: range×payload threshold rule |
| `src/aegis/knowledge_base/select.lp` | 21 | ✅ **Stub**: named Select Agent matching |
| `demos/app.py` | 267 | ✅ Three-pane Streamlit demo |
| `examples/benign_suzuki.py` | 55 | ✅ Clean ALLOW case |
| `examples/itar_turbopump_spec.md` | 49 | ✅ REFUSE via IV(h) inheritance |

### 🟡 Needed before first demo run

| Item | Why | Effort |
|---|---|---|
| `pyproject.toml` | uv sync / pip install | 5 min |
| `examples/hydrazine_protocol.py` | Propellant demo case (IV(h)(1)) | 10 min |
| `examples/edge_case_dual_use.md` | ESCALATE demo case | 15 min |
| `examples/ambiguous_component_spec.md` | Gap-driven ESCALATE | 10 min |
| `tests/test_golden.py` | 8–10 input→expected_decision pairs | 30 min |
| `src/aegis/cli.py` + entry point | `aegis check <file>` CLI | 20 min |
| End-to-end smoke test on local machine | Verify clingo actually solves | 15 min |

### 🔴 Known technical debt / risks

| Item | Severity | Mitigation |
|---|---|---|
| Proof-tree extraction enumerates derived atoms, doesn't walk rule-firing chain | Medium — judge who knows ASP may notice | Current output shows rule + premises + conclusion; upgrade to clingo's meta-programming post-hackathon |
| No embedding/vector layer for substance name → CAS resolution | Low — handled in extractor prompt with "never invent" guard | Add PubChem API lookup if time |
| Model string `claude-opus-4-5` in extractor defaults — confirm current production name | Low | Single `const.py` file, fix once |
| No CAD geometry parsing (STEP/IGES) | Out of scope by design | Stub returns low-confidence → triggers ESCALATE correctly |
| Clingo install sometimes gnarly on Windows | Medium | Document `uv add clingo` in README; have Docker fallback ready |

---

## Commit structure so far

The code was built top-down (models → pipeline → layers → KB → demo). For a clean git history before Claude Code takes over, suggested initial commits:

```
1. chore: scaffolding and pyproject
2. feat(models): core Pydantic data models
3. feat(extraction): protocol, design, prose extractors
4. feat(kb): USML Category IV with specially-designed inheritance
5. feat(kb): CWC/MTCR/Select Agent stubs
6. feat(reasoning): clingo engine with fact injection and gap detection
7. feat(decision): decision synthesis with LLM rationale and counterfactual
8. feat(integrations): aegis_guard decorator for ChemCrow/Coscientist
9. feat(demo): Streamlit three-pane UI
10. feat(examples): benign Suzuki + ITAR turbopump
```

---

## What depends on what (for parallelization)

If you and your partner want to split work, here's the dependency graph:

```
models.py ──┬─► extraction/* (can be built in parallel, all depend only on models)
            ├─► reasoning/engine.py ─► knowledge_base/*.lp (independent)
            └─► decision/synthesizer.py
                    ▲
                    └── integrations/ + demos/app.py (top-level, depend on everything)
```

- **You (ML/neural work):** extraction prompts, decision synthesizer, LLM evaluation
- **Partner (domain):** KB rules in `usml_cat_iv.lp`, example authoring, proof-tree validation

The KB is plain-text ASP — your partner can edit `.lp` files without touching Python.
