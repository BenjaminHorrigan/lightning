"""
LLM call abstraction for LIGHTNING.

Priority:
1. ANTHROPIC_API_KEY set  →  anthropic SDK (direct API)
2. claude CLI in PATH     →  Claude Code OAuth (Pro subscription)
3. RuntimeError with a clear message
"""
from __future__ import annotations

import os
import shutil
import subprocess

from lightning.const import DEFAULT_MODEL


def llm_call(
    system: str,
    user: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4096,
) -> str:
    """
    Make a single LLM call and return the response text.

    Routes through the Anthropic SDK if ANTHROPIC_API_KEY is set, otherwise
    calls the `claude` CLI which uses your Claude Code / Pro OAuth token.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if api_key:
        return _sdk_call(system, user, model, max_tokens, api_key)
    return _cli_call(system, user, model)


def _sdk_call(
    system: str, user: str, model: str, max_tokens: int, api_key: str
) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text.strip()


def _cli_call(system: str, user: str, model: str) -> str:
    """Route through `claude -p` using Claude Code's OAuth token."""
    claude_bin = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    if not os.path.isfile(str(claude_bin)):
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set and the claude CLI was not found. "
            "Either set ANTHROPIC_API_KEY or install Claude Code (https://claude.ai/code)."
        )

    result = subprocess.run(
        [
            str(claude_bin), "-p",
            "--model", model,
            "--output-format", "text",
            "--no-session-persistence",
            "--append-system-prompt", system,
            user,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"claude CLI exited {result.returncode}: {result.stderr[:400]}"
        )

    return result.stdout.strip()
