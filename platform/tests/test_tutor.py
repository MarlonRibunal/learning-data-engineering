"""Tests for the opt-in AI-tutor layer + its persisted settings.

No network: fake clients are injected. These lock what matters — the tutor is
off until opted in, it dispatches to the chosen provider, and it is always told
not to spoil.
"""

from __future__ import annotations

import pytest

from grader import settings, tutor
from grader.tutor import (
    PROVIDERS,
    TutorConfig,
    TutorRequest,
    TutorUnavailable,
    ask_tutor,
    build_user_content,
    resolve_config,
    tutor_available,
)


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


def _cfg(provider="anthropic", **over):
    base = dict(enabled=True, provider=provider, model="m", api_key="k")
    base.update(over)
    return TutorConfig(**base)


# ---- Anthropic double ----
class _Block:
    def __init__(self, text):
        self.text = text


class _AResp:
    def __init__(self, *texts):
        self.content = [_Block(t) for t in texts]


class _AMessages:
    def __init__(self, resp=None, error=None):
        self._resp, self._error, self.calls = resp, error, []

    def create(self, **kw):
        self.calls.append(kw)
        if self._error:
            raise self._error
        return self._resp


class _AnthropicClient:
    def __init__(self, resp=None, error=None):
        self.messages = _AMessages(resp, error)


# ---- OpenAI double ----
class _OAIMessage:
    def __init__(self, content):
        self.message = type("M", (), {"content": content})()


class _OAIResp:
    def __init__(self, content):
        self.choices = [_OAIMessage(content)]


class _OAICompletions:
    def __init__(self, resp=None, error=None):
        self._resp, self._error, self.calls = resp, error, []

    def create(self, **kw):
        self.calls.append(kw)
        if self._error:
            raise self._error
        return self._resp


class _OpenAIClient:
    def __init__(self, resp=None, error=None):
        self.chat = type("C", (), {"completions": _OAICompletions(resp, error)})()


# ---- settings persistence & config resolution -----------------------------

def test_settings_round_trip(tmp_path):
    assert settings.load(tmp_path) == {}
    settings.save(tmp_path, {"enabled": True, "provider": "openai", "model": "gpt-4o",
                             "api_key": "sk-x"})
    assert settings.load(tmp_path)["provider"] == "openai"


def test_corrupt_settings_never_raise(tmp_path):
    (tmp_path / settings.SETTINGS_FILENAME).write_text("{not json")
    assert settings.load(tmp_path) == {}


def test_prefs_theme_persists_separately_from_tutor(tmp_path):
    # theme prefs live in their own file, not the (0600, key-bearing) tutor file
    settings.save(tmp_path, {"theme": "Dark"}, settings.PREFS_FILENAME)
    settings.save(tmp_path, {"api_key": "sk-x"})  # tutor file, default name
    assert settings.load(tmp_path, settings.PREFS_FILENAME)["theme"] == "Dark"
    assert "theme" not in settings.load(tmp_path)          # not in the tutor file
    assert (tmp_path / settings.PREFS_FILENAME).is_file()  # survives a "restart" (fresh read)


def test_env_only_setup_enables_tutor(tmp_path, monkeypatch):
    monkeypatch.setenv(tutor.KEY_ENV, "sk-ant-env")
    cfg = resolve_config(tmp_path)
    assert cfg.enabled and cfg.api_key == "sk-ant-env"
    assert cfg.provider == "anthropic" and cfg.model == PROVIDERS["anthropic"]["default_model"]
    assert tutor_available(tmp_path) is True


def test_saved_toggle_overrides_and_off_hides_tutor(tmp_path, monkeypatch):
    monkeypatch.setenv(tutor.KEY_ENV, "sk-ant-env")  # key present...
    settings.save(tmp_path, {"enabled": False})       # ...but explicitly turned off
    assert tutor_available(tmp_path) is False


def test_saved_key_and_provider_win(tmp_path, monkeypatch):
    monkeypatch.delenv(tutor.KEY_ENV, raising=False)
    settings.save(tmp_path, {"enabled": True, "provider": "openai",
                             "model": "gpt-4o", "api_key": "sk-saved"})
    cfg = resolve_config(tmp_path)
    assert cfg.provider == "openai" and cfg.api_key == "sk-saved" and cfg.ready


def test_unknown_provider_falls_back(tmp_path):
    settings.save(tmp_path, {"enabled": True, "provider": "bogus", "api_key": "k"})
    assert resolve_config(tmp_path).provider == tutor.DEFAULT_PROVIDER


def test_no_key_means_unavailable(tmp_path, monkeypatch):
    monkeypatch.delenv(tutor.KEY_ENV, raising=False)
    assert tutor_available(tmp_path) is False


# ---- prompt construction (the anti-spoil guarantee) -----------------------

def test_system_prompt_forbids_the_solution():
    sp = tutor.SYSTEM_PROMPT.lower()
    assert "never" in sp
    assert "finished function" in sp and "full sql query" in sp


def test_user_content_carries_the_learners_actual_work():
    content = build_user_content(_req())
    assert "def scan_cost" in content
    assert "prices a query by bytes scanned" in content
    assert "1 TB = 1e12 bytes" in content
    assert "Do not write the solution" in content


def test_long_lesson_and_code_are_clipped():
    content = build_user_content(_req(lesson="x" * 9000, code="y" * 9000))
    assert "…(truncated)…" in content


# ---- dispatch (injected clients, no network) ------------------------------

def test_anthropic_dispatch_sends_no_spoil_system_prompt():
    client = _AnthropicClient(resp=_AResp("What unit is `b` in? A TB isn't a byte."))
    out = ask_tutor(_req(), config=_cfg("anthropic", model="claude-sonnet-5"), client=client)
    assert "TB" in out
    call = client.messages.calls[0]
    assert call["system"] is tutor.SYSTEM_PROMPT
    assert call["model"] == "claude-sonnet-5"


def test_openai_dispatch_puts_system_prompt_first():
    client = _OpenAIClient(resp=_OAIResp("Check the units on `b` before multiplying."))
    out = ask_tutor(_req(), config=_cfg("openai", model="gpt-4o"), client=client)
    assert "units" in out
    call = client.chat.completions.calls[0]
    assert call["model"] == "gpt-4o"
    assert call["messages"][0] == {"role": "system", "content": tutor.SYSTEM_PROMPT}
    assert call["messages"][1]["role"] == "user"


def test_disabled_config_raises():
    with pytest.raises(TutorUnavailable):
        ask_tutor(_req(), config=_cfg(enabled=False), client=_AnthropicClient(_AResp("x")))


def test_api_error_degrades_to_unavailable():
    client = _AnthropicClient(error=RuntimeError("network down"))
    with pytest.raises(TutorUnavailable):
        ask_tutor(_req(), config=_cfg(), client=client)


def test_empty_response_is_unavailable():
    for client in (_AnthropicClient(resp=_AResp()), _OpenAIClient(resp=_OAIResp(""))):
        with pytest.raises(TutorUnavailable):
            provider = "anthropic" if isinstance(client, _AnthropicClient) else "openai"
            ask_tutor(_req(), config=_cfg(provider), client=client)


def test_missing_config_and_repo_root_raises():
    with pytest.raises(TutorUnavailable):
        ask_tutor(_req())


def test_extract_helpers_handle_dict_shapes():
    assert tutor._anthropic_text(type("R", (), {"content": [{"text": "hi"}]})()) == "hi"
