"""Centralized constants. Edit DEFAULT_MODEL here, not across four files."""
from __future__ import annotations

import os


def _default_model() -> str:
    """
    Pick a default model ID that matches the active backend.

    Direct Anthropic API and Bedrock use different model identifier formats,
    so the default has to depend on which client get_client() will return.
    """
    # Lazy import keeps const.py free of intra-package cycles.
    from lightning._client import _use_bedrock
    if _use_bedrock():
        # Cross-region inference profile, US. Override with LIGHTNING_MODEL if
        # your Bedrock account/region exposes a different Claude variant.
        return "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    return "claude-sonnet-4-5"


DEFAULT_MODEL: str = os.environ.get("LIGHTNING_MODEL") or _default_model()
