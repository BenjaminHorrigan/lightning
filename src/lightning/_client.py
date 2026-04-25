"""
Anthropic client factory.

Picks AnthropicBedrock when AWS credentials are present in the environment,
otherwise falls back to the direct Anthropic API client. Both share the same
.messages.create() interface, so call sites don't have to care which backend
is in use.
"""
from __future__ import annotations

import os
from typing import Any


def get_client() -> Any:
    """Return a Messages-compatible client (AnthropicBedrock or Anthropic)."""
    if _use_bedrock():
        from anthropic import AnthropicBedrock
        return AnthropicBedrock(
            aws_region=os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1",
        )
    from anthropic import Anthropic
    return Anthropic()


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