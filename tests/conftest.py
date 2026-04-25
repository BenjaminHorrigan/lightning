"""
Patch get_client() to return None during tests so the deterministic rationale
fallback is used instead of making live LLM calls. Tests only check the
symbolic decision (ALLOW/REFUSE/ESCALATE), not the prose rationale.
"""
import pytest


@pytest.fixture(autouse=True)
def no_llm_client(monkeypatch):
    monkeypatch.setattr("lightning.decision.synthesizer.get_client", lambda: None)
