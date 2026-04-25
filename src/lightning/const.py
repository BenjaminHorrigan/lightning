"""Centralized constants. Edit DEFAULT_MODEL here, not across four files."""
from __future__ import annotations

import os

DEFAULT_MODEL: str = os.environ.get("AEGIS_MODEL", "claude-sonnet-4-6")
