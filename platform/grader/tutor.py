"""Optional AI-tutor layer — a personalized nudge on top of the offline hints.

The whole platform works with ZERO network: every rung ships an author-written
progressive hint ladder. This module adds an *opt-in* layer. When the learner
turns the tutor on (in the in-app Settings page, or via the LDE_TUTOR_KEY env
var) a failed check reveals an "Ask the tutor" button that sends their ACTUAL
code plus the exact grader failure to their chosen LLM and returns ONE Socratic
nudge — never the solution.

Design rules that keep it honest:

- **Offline-first.** No key, tutor toggled off, SDK package absent, or no network
  → the button doesn't appear (``tutor_available()`` is False) or the call raises
  ``TutorUnavailable`` and the UI keeps the offline ladder. Studying never breaks.
- **Bring your own model.** Anthropic (Claude) or OpenAI (GPT); the provider,
  model, and key are chosen in Settings and persisted on the state volume (see
  ``grader.settings``). Env vars act as defaults when nothing is saved.
- **Never spoils.** The system prompt forbids writing the answer, and the
  reference *solution* is deliberately NOT sent — there is nothing verbatim to
  leak. The tutor reasons from the lesson, the learner's code, the failure, and
  the author hints.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from . import settings

KEY_ENV = "LDE_TUTOR_KEY"
MODEL_ENV = "LDE_TUTOR_MODEL"
DEFAULT_PROVIDER = "anthropic"
_MAX_LESSON_CHARS = 2000
_MAX_CODE_CHARS = 4000

# The providers a learner can pick in Settings. Extend by adding an entry plus a
# dispatch function below — nothing else needs to change.
PROVIDERS: dict[str, dict] = {
    "anthropic": {
        "label": "Anthropic — Claude",
        "default_model": "claude-sonnet-5",
        "key_prefix": "sk-ant-",
        "package": "anthropic",
    },
    "openai": {
        "label": "OpenAI — GPT",
        "default_model": "gpt-4o",
        "key_prefix": "sk-",
        "package": "openai",
    },
}

SYSTEM_PROMPT = """\
You are the built-in tutor for a "learn data engineering by doing" course. A \
learner just failed an automated check on an exercise and asked for help. Give \
exactly ONE nudge that gets them unstuck — tuned to the specific code they wrote \
and the specific check that failed.

A good nudge:
- Names WHERE the problem is and points them at it, so they make the fix themselves.
- If their code is close, says what's already right, then the one thing to reconsider.
- If they've barely started (near-empty, or unchanged from the stub), points them \
to the idea in the lesson to try next — not to a "mistake".
- Leaves the doing to them. The struggle is where the learning happens.

Never:
- Write the corrected code, the finished function, or the full SQL query — not \
even "just change X to Y" when that single change is the whole answer.
- Simply restate the grader's error message; add insight beyond it.
- Pad with praise or preamble ("Great question!", "Sure!"). Get straight to the help.

You may name a concept, function, operator, or clause when it unlocks them — just \
don't assemble it into the working solution for them. Keep it to 2-4 sentences, \
plain and encouraging, and end with a small concrete next step they can take on \
their own.

You will be shown author-written hints for this exercise as the intended teaching \
direction. Follow their spirit, but respond to what the learner ACTUALLY wrote — \
if their mistake is somewhere the hints don't cover, address that instead."""


class TutorUnavailable(RuntimeError):
    """The tutor could not answer — off, no key, package missing, or the call failed.

    Always surfaced as "not available right now", never as a learner error: the
    UI catches this and falls back to the offline author hints.
    """


@dataclass
class TutorConfig:
    """The resolved, effective tutor configuration (Settings merged over env)."""

    enabled: bool
    provider: str
    model: str
    api_key: str

    @property
    def ready(self) -> bool:
        return self.enabled and bool(self.api_key.strip()) and self.provider in PROVIDERS


@dataclass
class TutorRequest:
    """Everything the tutor needs — assembled by the runner from the failed check."""

    title: str
    lesson: str
    code: str
    check_name: str
    grader_hint: str
    author_hints: list[str] = field(default_factory=list)


def resolve_config(repo_root: Path) -> TutorConfig:
    """Merge saved Settings over env defaults into the effective config.

    Precedence: a saved value wins; otherwise the env var; otherwise the
    provider default. ``enabled`` follows the saved toggle when present, else it
    defaults to on whenever a key exists (so an env-only headless setup works).
    """
    saved = settings.load(repo_root)
    provider = saved.get("provider") or DEFAULT_PROVIDER
    if provider not in PROVIDERS:
        provider = DEFAULT_PROVIDER
    api_key = (saved.get("api_key") or os.environ.get(KEY_ENV, "")).strip()
    model = (saved.get("model") or os.environ.get(MODEL_ENV, "")).strip() \
        or PROVIDERS[provider]["default_model"]
    enabled = bool(saved["enabled"]) if "enabled" in saved else bool(api_key)
    return TutorConfig(enabled=enabled, provider=provider, model=model, api_key=api_key)


def tutor_available(repo_root: Path) -> bool:
    """True only when the tutor is on AND has a key for a known provider."""
    return resolve_config(repo_root).ready


def _clip(text: str, limit: int) -> str:
    text = (text or "").strip()
    return text if len(text) <= limit else text[:limit] + "\n…(truncated)…"


def build_user_content(req: TutorRequest) -> str:
    """Render the learner's situation as the user turn. Pure — unit-tested."""
    hints = "\n".join(f"  {i}. {h}" for i, h in enumerate(req.author_hints, 1))
    parts = [
        f"# Exercise: {req.title}".strip(),
        "\n## Lesson\n" + _clip(req.lesson, _MAX_LESSON_CHARS),
        "\n## The learner's current submission\n```\n"
        + _clip(req.code, _MAX_CODE_CHARS)
        + "\n```",
        f"\n## The check that failed\n{req.check_name}"
        + (f" — {req.grader_hint}" if req.grader_hint else ""),
    ]
    if hints:
        parts.append("\n## Author hints (intended teaching direction)\n" + hints)
    parts.append(
        "\nGive the learner one Socratic nudge about their specific mistake. "
        "Do not write the solution."
    )
    return "\n".join(parts)


def ask_tutor(req: TutorRequest, *, repo_root: Path | None = None,
              config: TutorConfig | None = None, client=None) -> str:
    """Ask the configured LLM for one nudge. Returns the tutor's text.

    Raises ``TutorUnavailable`` for anything the learner shouldn't see as their
    own failure: tutor off, no key, package missing, or an API error. ``client``
    is injectable so tests never touch the network; ``config`` can be passed
    directly, otherwise it is resolved from ``repo_root``.
    """
    if config is None:
        if repo_root is None:
            raise TutorUnavailable("No tutor config or repo_root provided.")
        config = resolve_config(repo_root)
    if not config.enabled:
        raise TutorUnavailable("The AI tutor is turned off — enable it in Settings.")
    if config.provider not in PROVIDERS:
        raise TutorUnavailable(f"Unknown provider {config.provider!r} — pick one in Settings.")
    if client is None and not config.api_key.strip():
        raise TutorUnavailable("No API key set — add one in Settings.")
    return _DISPATCH[config.provider](req, config, client)


# ---- providers ------------------------------------------------------------

def _ask_anthropic(req: TutorRequest, config: TutorConfig, client) -> str:
    if client is None:
        try:
            import anthropic  # lazy: absent in a pure-offline install
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise TutorUnavailable(
                "The 'anthropic' package isn't installed. Run `pip install anthropic`."
            ) from exc
        client = anthropic.Anthropic(api_key=config.api_key)
    try:
        resp = client.messages.create(
            model=config.model,
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_content(req)}],
        )
    except Exception as exc:  # noqa: BLE001 - any SDK/network error → graceful fallback
        raise TutorUnavailable(f"The tutor couldn't be reached: {exc}") from exc
    text = _anthropic_text(resp)
    if not text:
        raise TutorUnavailable("The tutor returned an empty response.")
    return text


def _ask_openai(req: TutorRequest, config: TutorConfig, client) -> str:
    if client is None:
        try:
            import openai  # lazy
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise TutorUnavailable(
                "The 'openai' package isn't installed. Run `pip install openai`."
            ) from exc
        client = openai.OpenAI(api_key=config.api_key)
    try:
        resp = client.chat.completions.create(
            model=config.model,
            max_tokens=400,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_content(req)},
            ],
        )
    except Exception as exc:  # noqa: BLE001
        raise TutorUnavailable(f"The tutor couldn't be reached: {exc}") from exc
    text = _openai_text(resp)
    if not text:
        raise TutorUnavailable("The tutor returned an empty response.")
    return text


_DISPATCH = {"anthropic": _ask_anthropic, "openai": _ask_openai}


def _anthropic_text(resp) -> str:
    """Pull text from an Anthropic Messages response (or a test double)."""
    blocks = getattr(resp, "content", None) or []
    out = []
    for block in blocks:
        piece = getattr(block, "text", None)
        if piece is None and isinstance(block, dict):
            piece = block.get("text")
        if piece:
            out.append(piece)
    return "\n".join(out).strip()


def _openai_text(resp) -> str:
    """Pull text from an OpenAI chat completion (or a test double)."""
    try:
        message = resp.choices[0].message
    except (AttributeError, IndexError, TypeError):
        return ""
    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content")
    return (content or "").strip()
