"""
Anthropic client factory.

Priority:
1. AnthropicBedrock  — when AWS credentials are present
2. Anthropic SDK     — when ANTHROPIC_API_KEY is set
3. Claude CLI        — when running under Claude Code / Pro subscription

All three expose the same .messages.create() interface so call sites don't
have to care which backend is active.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any


def get_client() -> Any:
    """Return a Messages-compatible client."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    if _use_bedrock():
        from anthropic import AnthropicBedrock
        return AnthropicBedrock(
            aws_region=os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1",
        )
    if os.environ.get("ANTHROPIC_API_KEY", "").strip():
        from anthropic import Anthropic
        return Anthropic()
    # Fall back to the local claude CLI (works with Claude Pro / Claude Code OAuth)
    return _CliClient()


def _use_bedrock() -> bool:
    """
    Decide which backend to use:
      - LIGHTNING_USE_BEDROCK explicit (1/true/yes or 0/false/no) wins
      - AWS_BEARER_TOKEN_BEDROCK is unambiguous Bedrock-only auth → use Bedrock
      - AWS sigv4 creds present without an Anthropic key → use Bedrock
      - Otherwise → direct Anthropic API
    """
    flag = os.environ.get("LIGHTNING_USE_BEDROCK", "").lower()
    if flag in ("1", "true", "yes"):
        return True
    if flag in ("0", "false", "no"):
        return False
    if os.environ.get("AWS_BEARER_TOKEN_BEDROCK"):
        return True
    has_aws = bool(os.environ.get("AWS_ACCESS_KEY_ID"))
    has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return has_aws and not has_anthropic


# ---------------------------------------------------------------------------
# CLI backend — wraps `claude -p` to look like an Anthropic SDK client
# ---------------------------------------------------------------------------

class _FakeContent:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.content = [_FakeContent(text)]


class _MessagesResource:
    def create(
        self,
        model: str,
        max_tokens: int,
        messages: list,
        system: str = "",
        **kwargs,
    ) -> _FakeResponse:
        user_content = messages[0]["content"] if messages else ""
        claude_bin = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
        if not os.path.isfile(str(claude_bin)):
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set and the claude CLI was not found. "
                "Set ANTHROPIC_API_KEY or install Claude Code (https://claude.ai/code)."
            )
        result = subprocess.run(
            [
                str(claude_bin), "-p",
                "--model", model,
                "--output-format", "text",
                "--no-session-persistence",
                "--append-system-prompt", system,
                user_content,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"claude CLI exited {result.returncode}: {result.stderr[:400]}"
            )
        return _FakeResponse(result.stdout.strip())


class _CliClient:
    """Drop-in replacement for anthropic.Anthropic() that routes through the CLI."""
    def __init__(self) -> None:
        self.messages = _MessagesResource()
