"""
LIGHTNING command-line entry point.

    lightning check <file>

Runs the full pipeline on a file and pretty-prints the ClassificationResult.
Intended for quick demos and CI; the Streamlit app in demos/app.py is the
primary interactive surface.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from lightning import check
from lightning.models import Decision

app = typer.Typer(
    name="lightning",
    help="Neurosymbolic safety layer for autonomous research agents.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


DECISION_STYLES = {
    Decision.ALLOW:    ("green",  "ALLOW"),
    Decision.REFUSE:   ("red",    "REFUSE"),
    Decision.ESCALATE: ("yellow", "ESCALATE"),
}


@app.command("check")
def check_cmd(
    input_file: Path = typer.Argument(..., exists=True, readable=True,
                                      help="File to classify (protocol, spec, or proposal)"),
    json_output: bool = typer.Option(False, "--json",
                                     help="Emit the full ClassificationResult as JSON"),
    hint: Optional[str] = typer.Option(None, "--hint",
                                       help="Extractor hint: 'opentrons', 'autoprotocol'"),
) -> None:
    """Classify a single file and print the decision, proof, and citations."""
    text = input_file.read_text()

    try:
        result = check(text, hint=hint)
    except Exception as exc:  # surface cleanly instead of a traceback for the CLI
        console.print(f"[bold red]LIGHTNING failed to classify {input_file}:[/bold red] {exc}")
        raise typer.Exit(code=2)

    if json_output:
        typer.echo(result.model_dump_json(indent=2))
        raise typer.Exit(code=_exit_code(result.decision))

    _render_result(input_file, result)
    raise typer.Exit(code=_exit_code(result.decision))


def _exit_code(decision: Decision) -> int:
    """ALLOW=0, ESCALATE=1, REFUSE=2. Lets shell pipelines branch on it."""
    return {Decision.ALLOW: 0, Decision.ESCALATE: 1, Decision.REFUSE: 2}[decision]


def _render_result(path: Path, result) -> None:
    color, label = DECISION_STYLES[result.decision]

    console.rule(f"[bold]LIGHTNING[/bold]  {path.name}")

    headline = Text(f"  {label}  ", style=f"bold white on {color}")
    conf = Text(f"  confidence {result.confidence:.2f}", style="dim")
    console.print(headline + conf)
    console.print()

    console.print(Panel(result.artifact_summary, title="Artifact", expand=False))
    console.print(Panel(result.rationale, title="Rationale", style=color, expand=False))

    if result.primary_citations:
        table = Table(title="Primary citations", show_header=True, header_style="bold")
        table.add_column("Regime")
        table.add_column("Category")
        table.add_column("Reference")
        table.add_column("Text", overflow="fold")
        for c in result.primary_citations:
            table.add_row(c.regime.value, c.category, c.cfr_reference or "—", c.text[:160])
        console.print(table)

    if result.proof_tree.steps:
        console.print(Panel(_format_proof(result.proof_tree),
                            title="Proof tree", expand=False))

    if result.proof_tree.gaps:
        console.print(Panel("\n".join(f"• {g}" for g in result.proof_tree.gaps),
                            title="Gaps", style="yellow", expand=False))

    if result.counterfactual:
        console.print(Panel(result.counterfactual, title="Counterfactual",
                            style="blue", expand=False))

    if result.escalation_reason:
        console.print(Panel(result.escalation_reason, title="Escalation reason",
                            style="yellow", expand=False))

    console.print()
    console.print(f"[dim]regimes checked: {', '.join(r.value for r in result.regimes_checked)}[/dim]")


def _format_proof(proof) -> str:
    lines = []
    if proof.top_level_classification:
        lines.append(f"classification: {proof.top_level_classification}")
        lines.append("")
    for i, step in enumerate(proof.steps, start=1):
        lines.append(f"[{i}] rule: {step.rule_name}")
        for p in step.premises[:6]:
            lines.append(f"    ├─ premise: {p}")
        if len(step.premises) > 6:
            lines.append(f"    └─ … ({len(step.premises) - 6} more premises)")
        lines.append(f"    ⇒ {step.conclusion}")
        lines.append("")
    return "\n".join(lines).rstrip()


@app.command("regimes")
def regimes_cmd() -> None:
    """List the regulatory regimes LIGHTNING evaluates by default."""
    from lightning import DEFAULT_REGIMES
    from lightning.reasoning.engine import KB_MODULES
    table = Table(title="Default regimes")
    table.add_column("Regime")
    table.add_column("KB module")
    table.add_column("Depth")
    depth = {
        "USML": "deep — Category IV with 120.41 specially-designed inheritance",
        "CWC": "stub — named Schedule 1 + OP+F heuristic",
        "MTCR": "stub — range×payload threshold",
        "SELECT_AGENT": "stub — named list",
    }
    for r in DEFAULT_REGIMES:
        table.add_row(r.value, KB_MODULES.get(r, "—"), depth.get(r.value, "—"))
    console.print(table)


if __name__ == "__main__":
    app()
