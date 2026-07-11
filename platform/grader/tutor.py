"""Optional online AI-tutor layer — a personalized nudge on top of the offline floor.

The whole platform works with ZERO network: every rung ships an author-written
progressive hint ladder (see the runner's `_render_hints`). This module adds an
*opt-in* layer on top. When the learner exports an Anthropic API key as
``LDE_TUTOR_KEY``, a failed check reveals an "Ask the tutor" button that sends
their ACTUAL code plus the exact grader failure to Claude and returns ONE
Socratic nudge — never the solution.

Design rules that keep it honest:

- **Offline-first.** No key, no ``anthropic`` package, or no network → the button
  simply doesn't appear (``tutor_available()`` is False) or the call raises
  ``TutorUnavailable`` and the UI keeps the offline ladder. The feature can never
  break studying; it only ever adds to it.
- **Never spoils.** The system prompt forbids writing the answer. The learner's
  reference *solution* is deliberately NOT sent to the model — the tutor reasons
  from the lesson, the learner's code, the failure, and the author hints (which
  are already Socratic), so there is nothing verbatim to leak.
- **Grounded in THEIR work.** The nudge is about the specific code they wrote and
  the specific check that failed, not generic advice.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

KEY_ENV = "LDE_TUTOR_KEY"
MODEL_ENV = "LDE_TUTOR_MODEL"
DEFAULT_MODEL = "claude-sonnet-5"
_MAX_LESSON_CHARS = 2000
_MAX_CODE_CHARS = 4000

SYSTEM_PROMPT = """\
You are a warm, patient programming tutor inside a "learn data engineering by \
doing" platform. A learner is stuck: their submission just failed an automated \
grader check. Give ONE short, targeted hint that moves them a single step \
forward — grounded in the exact code they wrote and the exact failure.

Hard rules — never break these:
- NEVER write the corrected code, the finished function, or the full SQL query. \
Not even a one-line "just change X to Y" if that single change completes the \
answer. The struggle is where the learning happens; your job is to unblock, not \
to solve.
- Point at the SPECIFIC mistake in THEIR code. If they're close, say what is \
already right and where to look next.
- You may name a concept, an operator, or a function — but do not assemble it \
into the working solution for them.
- Ask a leading question when you can. Be concrete, not generic.
- 2–4 sentences. Encouraging, never condescending. No preamble, no sign-off.

You will be given author-written hints for this exercise. Treat them as the \
intended teaching direction, but respond to what the learner ACTUALLY wrote — \
if their error is somewhere the canned hints don't cover, address that instead."""


class TutorUnavailable(RuntimeError):
    """The tutor could not answer — no key, package missing, or the API call failed.

    Always surfaced as "not available right now", never as a learner error: the
    UI catches this and falls back to the offline author hints.
    """


@dataclass
class TutorRequest:
    """Everything the tutor needs — assembled by the runner from the failed check."""

    title: str
    lesson: str
    code: str
    check_name: str
    grader_hint: str
    author_hints: list[str] = field(default_factory=list)


def tutor_available() -> bool:
    """True if the learner has opted in by exporting an Anthropic key."""
    return bool(os.environ.get(KEY_ENV, "").strip())


def _model() -> str:
    return os.environ.get(MODEL_ENV, "").strip() or DEFAULT_MODEL


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


def ask_tutor(req: TutorRequest, *, client=None, model: str | None = None) -> str:
    """Ask Claude for one nudge. Returns the tutor's text.

    Raises ``TutorUnavailable`` for any reason the learner shouldn't see as a
    failure of their own: missing key, missing ``anthropic`` package, or an API
    error. ``client`` is injectable so tests never touch the network.
    """
    if client is None:
        key = os.environ.get(KEY_ENV, "").strip()
        if not key:
            raise TutorUnavailable(
                f"Set {KEY_ENV} to your Anthropic API key to enable the tutor."
            )
        try:
            import anthropic  # lazy: absent in a pure-offline install
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise TutorUnavailable(
                "The 'anthropic' package isn't installed. Run "
                "`pip install anthropic` to enable the tutor."
            ) from exc
        client = anthropic.Anthropic(api_key=key)

    try:
        resp = client.messages.create(
            model=model or _model(),
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_content(req)}],
        )
    except Exception as exc:  # noqa: BLE001 - any SDK/network error → graceful fallback
        raise TutorUnavailable(f"The tutor couldn't be reached: {exc}") from exc

    text = _extract_text(resp)
    if not text:
        raise TutorUnavailable("The tutor returned an empty response.")
    return text


def _extract_text(resp) -> str:
    """Pull the text out of a Messages response (or a test double)."""
    blocks = getattr(resp, "content", None) or []
    out = []
    for block in blocks:
        piece = getattr(block, "text", None)
        if piece is None and isinstance(block, dict):
            piece = block.get("text")
        if piece:
            out.append(piece)
    return "\n".join(out).strip()
