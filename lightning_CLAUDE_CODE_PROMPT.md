# Claude Code Handoff Prompt for AEGIS

Copy everything below the divider into Claude Code as your first message. It provides full context so Claude Code can start productively without you re-explaining.

---

You are taking over an in-progress hackathon project called **AEGIS** — a neurosymbolic safety layer for autonomous research agents. I'm preparing it for the SCSP AI+Expo Hackathon 2026 (Cloud Laboratories track). The submission window is **Sat April 25, 10am → Sun April 26, 6pm Pacific**. I have this week (today through April 24) to prepare, and the hackathon organizers have explicitly confirmed that **prior work, scaffolding, and research are fair game**.

## One-line pitch

A neurosymbolic safety layer that sits between autonomous research agents (ChemCrow, Coscientist, Virtual Lab) and the physical world. It extracts structured meaning from protocols/designs/proposals, reasons formally over export-control and dual-use regulations using an ASP solver, and returns auditable ALLOW/REFUSE/ESCALATE decisions with full proof trees.

## Why it wins

The SCSP hackathon is judged on four criteria: Novelty, Technical Difficulty, Potential Impact, Problem-Solution Fit. Most teams will build LLM + RAG + tool use and stop there. AEGIS's differentiation is a **real symbolic reasoning layer** (clingo/ASP) doing formal inference over regulatory ontologies. The LLM handles messy natural-language I/O; the symbolic layer handles decisions that require auditability. The demo includes a side-by-side kill shot where GPT-5 confidently hallucinates a classification and AEGIS refuses with a formal proof tree.

## Scope (already decided, don't revisit without strong reason)

- **Primary input:** protocols/code (Opentrons Python, Autoprotocol JSON) — deep support
- **Primary regime:** ITAR USML Category IV (rockets/missiles/launch vehicles) — deep encoding including the "specially designed" inheritance logic from 22 CFR 120.41
- **Stubs for extensibility claim:** CWC Schedule 1 (SMARTS-pattern matching is v2), MTCR (range×payload thresholds), Select Agents (organism list), design artifacts (text specs work, CAD stubbed), natural-language proposals
- **Primary deployment narrative:** front-end safety layer for autonomous research agents

## Team

- Me: ML practitioner, solid on Python and LLMs, learning Answer Set Programming this week
- Partner: rocket/research-lab experience, part-time contributor (a few hours/day this week, full commitment on hack weekend). Domain expertise is the load-bearing asset for ITAR encoding accuracy.

## What's already built (in this repo)

Read `.handoff/STATUS.md` first — it has a full file-by-file inventory with line counts and completion status. Summary: 17 files, ~2,300 lines of code + KB. The core pipeline is structurally complete:

- Data models (`models.py`) — done
- Three extractors (`extraction/protocol.py`, `design.py`, `prose.py`) — done
- Clingo reasoning engine (`reasoning/engine.py`) — done
- USML Category IV knowledge base (`knowledge_base/usml_cat_iv.lp`) — deep, 160 lines of ASP including specially-designed inheritance
- Stub KBs for CWC/MTCR/Select Agents — done
- Decision synthesizer with LLM rationale + counterfactual — done
- ChemCrow integration shim (`aegis_guard` decorator) — done
- Streamlit three-pane demo UI — done
- Two example inputs (benign Suzuki coupling, ITAR turbopump spec) — done

## What I need you to do, in order

### Phase 1 — Make it run (highest priority, this session)

1. Create `pyproject.toml` with uv-compatible config. Dependencies: `anthropic`, `clingo`, `pydantic>=2`, `streamlit`, `rdkit`, `python-dotenv`. Python 3.11+.
2. Create `.env.example` with `ANTHROPIC_API_KEY=` placeholder.
3. Verify the package structure imports cleanly (`uv sync && uv run python -c "from aegis import check"`).
4. Run the benign Suzuki example end-to-end. Fix any integration issues you find — there will be some. The clingo output parsing in `reasoning/engine.py` is the likeliest source of bugs.
5. Run the ITAR turbopump example end-to-end. It should produce REFUSE with a USML IV(h) citation.
6. If anything fails, fix it before moving on. Do not add features until the existing examples work.

### Phase 2 — Finish the demo set (after Phase 1 passes)

Create these three example files. They are the scripted inputs for demo day and need to produce predictable decisions:

1. `examples/hydrazine_protocol.py` — Opentrons-style protocol for a reaction involving hydrazine (CAS 302-01-2) as a reagent. Should trigger `USML_IV_h_propellant` classification. REFUSE with citation to 22 CFR 121.1 Category IV(h)(1). Keep it realistic — published hydrazine chemistry exists, use something plausible.

2. `examples/edge_case_dual_use.md` — a research proposal that's genuinely ambiguous. The proposal should describe research that *could* have either civilian or controlled applications (e.g., high-energy-density materials research that might or might not have propellant end-use). Should trigger ESCALATE via the `stated_intent` / `inferred_intent` gap mechanism. This is the demo moment that shows judges we handle nuance, not just binary cases.

3. `examples/ambiguous_component_spec.md` — an engineering spec for a turbopump or nozzle with NO `parent_system` specified. Should trigger ESCALATE via the gap-detection logic in `reasoning/engine.py` (`_identify_gaps`). Demonstrates the reasoner correctly identifying what it cannot conclude.

### Phase 3 — Eval harness and CLI

4. Create `tests/test_golden.py` with pytest. 10 hand-curated (input_path, expected_decision) pairs using the example files and 4-5 additional synthetic cases. This gives us a regression harness before we start tuning extraction prompts.

5. Create `src/aegis/cli.py` with a `click` or `typer`-based CLI. Entry point `aegis check <file>` that runs the pipeline and pretty-prints the result. Wire it into `pyproject.toml` `[project.scripts]`.

### Phase 4 — Polish (only after Phases 1-3 are solid)

6. Review `reasoning/engine.py` — the proof-tree extraction currently enumerates derived atoms rather than walking the rule-firing chain. Upgrade it using clingo's meta-programming features so the proof tree shows true reasoning steps. This is technical-difficulty scoring fuel.
7. Tighten extraction prompts based on golden test results.
8. Improve Streamlit UI per the mockups in `.handoff/ui_mockups.md`.

## Strict constraints

- **Do not refactor the architecture** without explicit buy-in. The scope (primary regime + primary input + stubs for others) is deliberate and was chosen after pushback discussion.
- **The symbolic layer never calls the LLM**, and the LLM never overrides the symbolic decision. This is a core trust property. The LLM's roles are (a) extraction, (b) rationale prose generation, (c) counterfactual prose — nothing else. Do not introduce LLM-based classification anywhere in the decision path.
- **Citations must always be real.** The `citations.json` table is the source of truth. Never let the LLM invent a CFR reference.
- **Prefer simplicity over cleverness** in code Claude Code writes. This repo must stay readable to me and my partner through the hack weekend.
- Use `uv` (not pip/poetry). Python 3.11+. Type hints everywhere.

## How to work with me

- Start by reading `.handoff/STATUS.md`, `README.md`, and `src/aegis/models.py` in that order. That's ~500 lines and gives you the whole context.
- When you identify issues, state them first, then propose fixes before implementing wide-ranging changes.
- Commit in the logical units suggested in `STATUS.md`.
- If something looks wrong with the ASP encoding in `usml_cat_iv.lp`, flag it — I need to flag back to my partner who has the domain knowledge rather than fix it blindly.

## First action

Read `.handoff/STATUS.md`, then `README.md`, then `src/aegis/models.py`. Then report back with:
1. Your understanding of the architecture in ≤150 words
2. Top 3 issues you expect to hit in Phase 1
3. Confirmation before starting Phase 1

Go.
