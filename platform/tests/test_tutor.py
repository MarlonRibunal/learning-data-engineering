"""Tests for the opt-in AI-tutor layer.

No network: a fake client is injected. These lock the two things that matter —
the tutor never runs without opt-in, and it is always told not to spoil.
"""

from __future__ import annotations

import pytest

from grader import tutor
from grader.tutor import TutorRequest, TutorUnavailable, ask_tutor, build_user_content


def _req(**over):
    base = dict(
        title="Cloud: what a query costs",
        lesson="Serverless warehouses bill per byte scanned.",
        code="def scan_cost(b, p):\n    return b * p  # wrong: bytes, not TB",
        check_name="prices a query by bytes scanned",
        grader_hint="expected 10.0, got 1e13",
        author_hints=["units don't line up", "1 TB = 1e12 bytes"],
    )
    base.update(over)
    return TutorRequest(**base)


class _FakeMessages:
    def __init__(self, resp=None, error=None):
        self._resp, self._error, self.calls = resp, error, []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self._error:
            raise self._error
        return self._resp


class _FakeClient:
    def __init__(self, resp=None, error=None):
        self.messages = _FakeMessages(resp, error)


class _Block:
    def __init__(self, text):
        self.text = text


class _Resp:
    def __init__(self, *texts):
        self.content = [_Block(t) for t in texts]


# ---- availability / opt-in ------------------------------------------------

def test_unavailable_without_key(monkeypatch):
    monkeypatch.delenv(tutor.KEY_ENV, raising=False)
    assert tutor.tutor_available() is False


def test_available_with_key(monkeypatch):
    monkeypatch.setenv(tutor.KEY_ENV, "sk-ant-xxx")
    assert tutor.tutor_available() is True


def test_ask_without_key_or_client_raises(monkeypatch):
    monkeypatch.delenv(tutor.KEY_ENV, raising=False)
    with pytest.raises(TutorUnavailable):
        ask_tutor(_req())


# ---- prompt construction (the anti-spoil guarantee) -----------------------

def test_system_prompt_forbids_the_solution():
    sp = tutor.SYSTEM_PROMPT.lower()
    assert "never write the corrected code" in sp
    assert "full sql query" in sp or "finished function" in sp


def test_user_content_carries_the_learners_actual_work():
    content = build_user_content(_req())
    assert "def scan_cost" in content            # their code
    assert "prices a query by bytes scanned" in content  # the failed check
    assert "1 TB = 1e12 bytes" in content        # author hints as direction
    assert "Do not write the solution" in content


def test_long_lesson_and_code_are_clipped():
    content = build_user_content(_req(lesson="x" * 9000, code="y" * 9000))
    assert "…(truncated)…" in content


# ---- the call (injected client, no network) -------------------------------

def test_ask_tutor_returns_text_and_passes_guardrails():
    client = _FakeClient(resp=_Resp("What unit is `b` in? A terabyte isn't one byte."))
    out = ask_tutor(_req(), client=client, model="claude-sonnet-5")
    assert "terabyte" in out
    call = client.messages.calls[0]
    assert call["system"] is tutor.SYSTEM_PROMPT      # always sent the no-spoil system prompt
    assert call["model"] == "claude-sonnet-5"
    assert call["messages"][0]["role"] == "user"


def test_api_error_degrades_to_unavailable():
    client = _FakeClient(error=RuntimeError("network down"))
    with pytest.raises(TutorUnavailable):
        ask_tutor(_req(), client=client)


def test_empty_response_is_unavailable():
    client = _FakeClient(resp=_Resp())
    with pytest.raises(TutorUnavailable):
        ask_tutor(_req(), client=client)


def test_extract_text_handles_dict_blocks():
    assert tutor._extract_text(type("R", (), {"content": [{"text": "hi"}]})()) == "hi"
