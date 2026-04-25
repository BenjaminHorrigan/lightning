"""
ChemCrow integration shim.

This is the "deployment story" code. The entire pitch lands on this:

    from lightning.integrations.chemcrow import lightning_guard
    from chemcrow import ChemCrow

    agent = ChemCrow()
    safe_agent = lightning_guard(agent)  # <-- one line

    safe_agent.run("Synthesize hydrazine N2H4")
    # LIGHTNING intercepts, classifies under USML IV(h)(1), refuses with citation.

The decorator wraps any callable that generates protocols or chemistry actions.
It intercepts the output BEFORE it reaches the lab, runs LIGHTNING, and either
passes through (ALLOW), raises (REFUSE), or returns an escalation handle
(ESCALATE).

This works for ChemCrow, Coscientist, Virtual Lab, or any agent whose final
output is a protocol or action sequence.
"""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Optional

from lightning import check
from lightning.models import Decision


class LightningRefusal(Exception):
    """
    Raised when LIGHTNING refuses to pass an artifact through to execution.

    Contains the full ClassificationResult so the caller can log, display,
    or route to human review.
    """
    def __init__(self, result):
        self.result = result
        citations = ", ".join(
            f"{c.regime.value} {c.category}" for c in result.primary_citations
        )
        super().__init__(
            f"LIGHTNING refused: {result.rationale} "
            f"[Citations: {citations}]"
        )


class LightningEscalation(Exception):
    """
    Raised when LIGHTNING cannot make a decisive call and requires human review.
    """
    def __init__(self, result):
        self.result = result
        super().__init__(
            f"LIGHTNING escalation: {result.escalation_reason}"
        )


def lightning_guard(
    agent_or_function: Any,
    refuse_mode: str = "raise",  # "raise" | "return" | "log_only"
    escalate_mode: str = "raise",
    on_refuse: Optional[Callable] = None,
    on_escalate: Optional[Callable] = None,
) -> Any:
    """
    Wrap an agent or function so that its outputs are screened by LIGHTNING
    before being returned.

    Args:
        agent_or_function: a callable, or an object with a .run() method
        refuse_mode: what to do on REFUSE — "raise" (LightningRefusal), "return"
            (return the ClassificationResult), or "log_only" (pass through
            anyway, logging the refusal; dangerous, for debugging only)
        escalate_mode: same options, for ESCALATE decisions
        on_refuse: optional callback invoked on refusal
        on_escalate: optional callback invoked on escalation
    """
    # Case 1: wrapping an object with a .run() method (agent-style)
    if hasattr(agent_or_function, "run") and callable(agent_or_function.run):
        original_run = agent_or_function.run

        @wraps(original_run)
        def guarded_run(*args, **kwargs):
            output = original_run(*args, **kwargs)
            return _screen_output(
                output, refuse_mode, escalate_mode, on_refuse, on_escalate
            )

        agent_or_function.run = guarded_run
        return agent_or_function

    # Case 2: wrapping a function directly
    if callable(agent_or_function):
        @wraps(agent_or_function)
        def guarded(*args, **kwargs):
            output = agent_or_function(*args, **kwargs)
            return _screen_output(
                output, refuse_mode, escalate_mode, on_refuse, on_escalate
            )
        return guarded

    raise TypeError(
        f"lightning_guard expected a callable or an object with .run(), "
        f"got {type(agent_or_function).__name__}"
    )


def _screen_output(
    output: Any,
    refuse_mode: str,
    escalate_mode: str,
    on_refuse: Optional[Callable],
    on_escalate: Optional[Callable],
) -> Any:
    """Run LIGHTNING on an agent output and handle the decision."""
    # Normalize output to something check() accepts
    if not isinstance(output, (str, dict)):
        output_str = str(output)
    else:
        output_str = output

    result = check(output_str)

    if result.decision == Decision.ALLOW:
        return output

    if result.decision == Decision.REFUSE:
        if on_refuse:
            on_refuse(result)
        if refuse_mode == "raise":
            raise LightningRefusal(result)
        if refuse_mode == "return":
            return result
        if refuse_mode == "log_only":
            print(f"[LIGHTNING] REFUSE logged (log_only mode): {result.rationale}")
            return output

    if result.decision == Decision.ESCALATE:
        if on_escalate:
            on_escalate(result)
        if escalate_mode == "raise":
            raise LightningEscalation(result)
        if escalate_mode == "return":
            return result
        if escalate_mode == "log_only":
            print(f"[LIGHTNING] ESCALATE logged (log_only mode): {result.escalation_reason}")
            return output

    return output


# Decorator form for convenience
def guard(func: Callable) -> Callable:
    """
    Decorator form:

        @guard
        def generate_protocol(request: str) -> str:
            ...  # your LLM-based protocol generator
    """
    return lightning_guard(func)
