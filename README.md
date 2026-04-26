# LIGHTNING

**A neurosymbolic safety layer for autonomous research agents.**

LIGHTNING sits between AI systems that generate technical artifacts (protocols, designs, proposals) and the physical or regulatory world they touch. It extracts structured meaning from unstructured inputs, reasons formally over export-control and dual-use regulations, and returns auditable allow/refuse/escalate decisions with full proof trees.

## Why this exists

Every autonomous research system shipped in the last two years has the same gap: no formal safety layer. Coscientist's own *Nature* paper included a dual-use appendix. ChemCrow has no export-control reasoning. Cloud labs (Emerald, Strateos) rely on human safety review that does not scale to agent-rate request volumes.

LIGHTNING is the missing layer. It is not a better research agent; it is what makes research agents deployable in regulated environments.

## Architecture

```
  Input (protocol, design, proposal)
         │
         ▼
  ┌─────────────────┐
  │  Extraction     │  Neural: LLM → structured TechnicalArtifact
  │  (neural)       │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  Reasoning      │  Symbolic: ASP (clingo) over regulatory KB
  │  (symbolic)     │  produces ProofTree across all active regimes
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  Decision       │  Hybrid: proof → rationale + counterfactual
  │  (hybrid)       │
  └────────┬────────┘
           │
           ▼
  ClassificationResult { decision, citations, proof, rationale }
```

**Core trust property:** The symbolic layer never calls the LLM. The LLM never overrides the symbolic decision. Extraction and rationale generation are the only LLM roles.

## Regulatory Coverage

All regimes run by default on every artifact. A single protocol or design is simultaneously evaluated across all applicable law.

### Active Regimes

| Regime | Authority | Substances / Article Types | Coverage |
|--------|-----------|---------------------------|----------|
| **USML Cat IV** | State Dept / ITAR | Rockets, missiles, propellants | Deep (22 CFR 121.1 IV(a)–(h)) |
| **USML Cat VIII** | State Dept / ITAR | Military aircraft, engines, parts | Deep (22 CFR 121.1 VIII(a)–(c)) |
| **USML Cat XIV** | State Dept / ITAR | Chemical/biological warfare agents | 33 agents |
| **USML Cat XV** | State Dept / ITAR | Military spacecraft, ground stations | Deep (22 CFR 121.1 XV(a)–(c)) |
| **USML Explosives** | State Dept / ITAR | Military explosives, warheads | 39 items |
| **CWC Schedule 1** | Commerce/State | Weapons-grade chemical agents | 21 substances (~100%) |
| **CWC Schedule 2** | Commerce/State | Precursor chemicals | 27 substances (~55%) |
| **CWC Schedule 3** | Commerce/State | Industrial dual-use chemicals | 32 substances (~90%) |
| **DEA Schedule I** | DOJ/DEA | High-abuse, no medical use | 36 substances |
| **DEA Schedule II** | DOJ/DEA | High-abuse, accepted medical use | 39 substances |
| **DEA Schedule III-V** | DOJ/DEA | Lower-risk controlled substances | 47 substances |
| **HHS Select Agents** | HHS/CDC (42 CFR 73) | Human pathogens and toxins | 53 agents (~80%) |
| **USDA Select Agents** | USDA (7 CFR 331) | Animal/plant pathogens | 43 agents (~95%) |
| **Australia Group Bio** | Multilateral | BWC-relevant pathogens | 48 agents (~45%) |
| **BIS Entity List** | Commerce/BIS | Export-restricted organizations | 40 entities |
| **BIS AI/Compute** | Commerce/BIS (EAR) | Advanced chips, quantum, HPC | 38 items |
| **EAR Category 1** | Commerce/BIS (EAR) | Dual-use advanced materials | 38 materials |
| **MTCR** | Multilateral | Missile/rocket range×payload | Parametric rules |

**Total: ~514 named substances/entities/article-types across 18 regimes.**

### Knowledge Base Structure

```
src/lightning/reasoning/rules/
├── _common/          # Cross-regime vocabulary (atom_vocabulary.lp, specially_designed.lp)
├── usml/             # ITAR USML rules
│   ├── cat_iv.lp           # Cat IV rockets/missiles — deep (specially-designed inheritance)
│   ├── cat_iv_propellants.lp
│   ├── cat_viii.lp         # Cat VIII military aircraft, engines, parts — deep
│   ├── cat_xiv_toxics_*.lp # Cat XIV chemical/biological warfare agents
│   ├── cat_xv.lp           # Cat XV military spacecraft, ground stations — deep
│   └── explosives_*.lp     # Military explosives and warheads
├── cwc/              # CWC Schedules 1-3
├── dea/              # DEA Schedules I-V
├── bwc_select_agents/# HHS, USDA, Australia Group biological agents
├── bis/              # EAR Entity List, AI/Compute, Category 1 materials
└── mtcr/             # MTCR parametric thresholds

data/sources/         # Authoritative CSV files (human-editable regulatory data)
data/atoms/           # Generated ASP atoms (do not edit by hand)
```

## Quickstart

```bash
# Setup
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# Streamlit demo (three-pane: input / proof tree / decision)
uv run streamlit run demos/app.py

# FastAPI server with web UI
uv run python demos/fastapi_app.py

# CLI
uv run lightning check examples/rocket_protocol.py

# Deterministic test suite (no API key needed)
uv run pytest tests/test_golden.py tests/test_proof_properties.py -q

# Full suite including LLM extraction tests (requires ANTHROPIC_API_KEY)
uv run pytest
```

Set `ANTHROPIC_API_KEY` in `.env` before running the demo or end-to-end tests.

## Repository layout

```
lightning/
├── src/lightning/
│   ├── extraction/         # Neural layer: LLM → TechnicalArtifact
│   │   ├── protocol.py     # Opentrons/Autoprotocol parser
│   │   ├── design.py       # CAD/spec parser
│   │   └── prose.py        # NL proposal parser
│   ├── reasoning/          # Symbolic layer: artifact → ProofTree
│   │   ├── engine.py       # Clingo wrapper, all-regime evaluation
│   │   └── rules/          # ASP knowledge base (see above)
│   ├── decision/           # Hybrid layer: proof → final decision
│   │   └── synthesizer.py  # Pure-symbolic _decide(); LLM for rationale only
│   ├── integrations/
│   │   └── chemcrow.py     # lightning_guard() one-liner for agent wrapping
│   └── models.py           # Pydantic contracts between all layers
├── data/
│   ├── sources/            # Regulatory CSVs (one per regime, human-maintained)
│   └── atoms/              # Generated ASP facts
├── scripts/
│   └── generate_substance_atoms.py  # CSV → ASP bulk loader
├── demos/
│   └── fastapi_app.py      # FastAPI server with web UI
├── examples/               # Sample inputs for each regime
└── tests/
    ├── test_golden.py          # Deterministic artifact-level regression tests (84 cases)
    └── test_proof_properties.py# LIGHTNING vs LLM: determinism, citations, proof chain
```

## Adding a new regime

1. Add a CSV to `data/sources/` and a config entry to `scripts/generate_substance_atoms.py`
2. Run `python scripts/generate_substance_atoms.py --regime <name>` to generate ASP atoms
3. Add classification rules to `src/lightning/reasoning/rules/<regime>/`
4. Add the regime to `REGIME_DIRS` in `reasoning/engine.py`
5. Add golden tests to `tests/test_golden.py`
