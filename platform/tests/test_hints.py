"""Tests for the progressive hint ladder (the stuck-buster).

Two layers: the persisted reveal counter (grader/progress.py, pure stdlib) and
the hint-selection logic in the runner (imported only if streamlit is present).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from grader import progress

REPO = Path(__file__).resolve().parents[2]
SCAN_COST = REPO / "projects/datamart-intelligence-platform/tasks/sprint-cloud/scan-cost/spec.yml"


def test_reveal_counter_escalates_and_persists(tmp_path):
    assert progress.hints_shown(tmp_path, "s", "t") == 0
    assert progress.reveal_hint(tmp_path, "s", "t") == 1
    assert progress.reveal_hint(tmp_path, "s", "t") == 2
    # Persisted to disk, so it survives a "power-down" (a fresh read).
    assert progress.hints_shown(tmp_path, "s", "t") == 2


def test_reveal_does_not_clobber_existing_progress(tmp_path):
    progress.record(tmp_path, "s", "t", "fail")
    progress.reveal_hint(tmp_path, "s", "t")
    state = progress.load(tmp_path)["s"]["t"]
    assert state["status"] == "fail"
    assert state["attempts"] == 1
    assert state["hints_shown"] == 1


def test_scan_cost_ships_a_full_hint_ladder():
    spec = yaml.safe_load(SCAN_COST.read_text())
    pyfunc = next(c for c in spec["checks"] if c["type"] == "pyfunc")
    hints = pyfunc["hints"]
    assert len(hints) == 3  # nudge -> concept -> near-answer
    # The near-answer stage names the concrete result; earlier ones must not.
    assert "10.0" in hints[-1]
    assert "10.0" not in hints[0]


def test_hint_selection_matches_the_failing_check():
    st = pytest.importorskip("streamlit")  # noqa: F841 - runner imports streamlit
    import sys

    sys.path.insert(0, str(REPO / "platform" / "runner"))
    import app  # type: ignore
    from grader.result import CheckResult, Result, Status

    spec = type("Spec", (), {"checks": [
        {"type": "file_exists", "name": "exists"},
        {"type": "pyfunc", "name": "prices it", "hints": ["one", "two"]},
    ]})()

    # Only the pyfunc check failed -> its hints are selected.
    failing = Result("s", "t", [
        CheckResult("exists", Status.PASS),
        CheckResult("prices it", Status.FAIL, "wrong"),
    ])
    assert app._failing_hints(spec, failing) == ["one", "two"]

    # Nothing failed -> no hints.
    passing = Result("s", "t", [CheckResult("prices it", Status.PASS)])
    assert app._failing_hints(spec, passing) == []
