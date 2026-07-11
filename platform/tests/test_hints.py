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


TASKS = REPO / "projects/datamart-intelligence-platform/tasks"
# Sprints whose rungs are high-friction enough that every one ships a hint
# ladder. Guards against a new rung landing here without one.
HINTED_SPRINTS = ["sprint-4-spark", "sprint-8-realtime", "streaming"]
LOGIC_TYPES = {"spark", "spark_streaming", "redpanda", "pyfunc"}


def _hinted_specs():
    specs = []
    for sprint in HINTED_SPRINTS:
        specs += sorted((TASKS / sprint).glob("*/spec.yml"))
    specs += [
        TASKS / "capstone/stateful-streaming/spec.yml",
        TASKS / "capstone/realtime-monitor/spec.yml",
    ]
    return specs


@pytest.mark.parametrize("spec_file", _hinted_specs(), ids=lambda p: f"{p.parent.parent.name}/{p.parent.name}")
def test_spark_and_streaming_rungs_ship_a_hint_ladder(spec_file):
    spec = yaml.safe_load(spec_file.read_text())
    logic = [c for c in spec["checks"] if c["type"] in LOGIC_TYPES]
    assert logic, f"{spec_file} has no logic check"
    # Every logic check (capstones have several) must carry a full 3-step ladder.
    for check in logic:
        hints = check.get("hints")
        assert hints and len(hints) == 3, f"{spec_file}: '{check.get('name')}' lacks a 3-hint ladder"
        assert all(isinstance(h, str) and h.strip() for h in hints)


# The foundational sprints beginners hit first. Each rung has the learner editing
# ONE file, so a single ladder rides the PRIMARY (first non-file_exists) check;
# secondary sql_assert/file_contains checks keep their own inline hint: one-liner.
FUNDAMENTALS_SPRINTS = [
    "sql-fundamentals", "ingestion", "data-quality", "sprint-2-dbt", "sprint-3-airflow",
]


def _fundamentals_specs():
    specs = []
    for sprint in FUNDAMENTALS_SPRINTS:
        specs += sorted((TASKS / sprint).glob("*/spec.yml"))
    return specs


@pytest.mark.parametrize("spec_file", _fundamentals_specs(), ids=lambda p: f"{p.parent.parent.name}/{p.parent.name}")
def test_fundamentals_rungs_ship_a_hint_ladder(spec_file):
    spec = yaml.safe_load(spec_file.read_text())
    logic = [c for c in spec["checks"] if c["type"] != "file_exists"]
    assert logic, f"{spec_file} has no logic check"
    primary = logic[0]
    hints = primary.get("hints")
    assert hints and len(hints) == 3, f"{spec_file}: primary '{primary.get('name')}' lacks a 3-hint ladder"
    assert all(isinstance(h, str) and h.strip() for h in hints)


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
