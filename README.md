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
  │  Reasoning      │  Symbolic: Datalog/ASP over regulatory KB
  │  (symbolic)     │  produces ProofTree
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

## Primary scope (v1)

- **Input modality:** protocols/code (Opentrons Python, Autoprotocol JSON)
- **Regulatory regime:** ITAR USML Category IV (launch vehicles, missiles, rockets)
- **Symbolic substrate:** Answer Set Programming via `clingo`

## Stub scope (architectural, not demo-critical)

- Input: CAD/specs (extractor exists, parsing is shallow)
- Input: natural-language proposals (extractor exists, intent inference is shallow)
- Regimes: CWC (SMARTS substructure matching, Schedule 1 only), MTCR (range×payload thresholds), Select Agents (organism list lookup)

## Quickstart

```bash
# Setup
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# Run the demo
uv run streamlit run demos/app.py

# Run the CLI
uv run lightning check examples/rocket_protocol.py
```

## Repository layout

```
lightning/
├── src/lightning/
│   ├── extraction/       # Neural layer: LLM → TechnicalArtifact
│   │   ├── protocol.py   # Opentrons/Autoprotocol parser
│   │   ├── design.py     # CAD/spec parser (stub)
│   │   └── prose.py      # NL proposal parser (stub)
│   ├── reasoning/        # Symbolic layer: artifact → ProofTree
│   │   ├── engine.py     # Clingo wrapper
│   │   ├── itar.py       # USML Category IV rules (deep)
│   │   ├── cwc.py        # CWC Schedule 1 (stub)
│   │   ├── mtcr.py       # MTCR thresholds (stub)
│   │   └── select.py     # Select Agents (stub)
│   ├── decision/         # Hybrid layer: proof → final decision
│   │   ├── synthesizer.py
│   │   └── counterfactual.py
│   ├── knowledge_base/   # Regulatory ground truth
│   │   ├── usml_cat_iv.lp    # ASP rules, encoded
│   │   ├── cwc_sched1.lp     # stub
│   │   └── citations.json    # regulation text + URLs
│   ├── integrations/     # Deployment shims
│   │   ├── chemcrow.py   # @lightning.guard decorator
│   │   ├── opentrons.py  # Pre-execution hook
│   │   └── api.py        # FastAPI server for agent-rate queries
│   └── models.py         # Pydantic data models
├── demos/
│   └── app.py            # Streamlit demo
├── examples/
│   ├── benign_suzuki.py
│   ├── itar_turbopump_spec.md
│   └── edge_case_dual_use.py
└── tests/
    └── test_golden.py    # Hand-curated eval set
```
