"""The runner's _CURRICULUM is the single source of truth for phases/sprints.
These guard that it stays consistent with the graded content on disk and the
grader's progression order, and that every sprint is fully described."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


def _app():
    pytest.importorskip("streamlit")
    sys.path.insert(0, str(REPO / "platform" / "runner"))
    import app  # type: ignore
    return app


def _sprints_in_discovery_order():
    from grader import discover_tasks
    seen = []
    for s, _ in discover_tasks(REPO):
        if s not in seen:
            seen.append(s)
    return seen


def test_curriculum_matches_discovered_sprints_in_order():
    app = _app()
    keys = [s["key"] for ph in app._CURRICULUM for s in ph["sprints"]]
    assert keys == _sprints_in_discovery_order(), \
        "curriculum order must match the on-disk sprint discovery order"


def test_curriculum_order_matches_grader_sprint_order():
    app = _app()
    from grader.core import _SPRINT_ORDER
    keys = [s["key"] for ph in app._CURRICULUM for s in ph["sprints"] if s["key"] != "capstone"]
    assert keys == list(_SPRINT_ORDER)


def test_every_phase_and_sprint_is_fully_described():
    app = _app()
    assert len(app._CURRICULUM) == 5  # Foundations, Scaling, Real-time, Production, Capstone
    for ph in app._CURRICULUM:
        assert ph.get("title") and ph.get("intro")
        assert ph["sprints"]
        for s in ph["sprints"]:
            assert s.get("name") and s.get("stage")
            assert s.get("focus"), f"{s['key']} missing focus"
            assert s.get("skills"), f"{s['key']} missing skills"
            assert s.get("intro"), f"{s['key']} missing sub-intro"
