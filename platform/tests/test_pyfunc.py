"""Tests for the `pyfunc` check + the dashboard sprint. Pure Python (runs in CI)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from grader.checks.pyfunc import PyFuncCheck, _norm
from grader.context import Context
from grader.registry import REGISTRY
from grader.result import Status

REPO = Path(__file__).resolve().parents[2]
TASKS = REPO / "projects/datamart-intelligence-platform/tasks/sprint-9-dashboard"
# (task dir, submission filename)
ALL_TASKS = [
    ("kpi-cards", "kpi_cards.py"),
    ("revenue-by-day", "revenue_by_day.py"),
    ("top-categories", "top_categories.py"),
    ("pct-change", "pct_change.py"),
    ("running-total", "running_total.py"),
    ("threshold-status", "health_status.py"),
]


def _spec(task: str) -> dict:
    spec = yaml.safe_load((TASKS / task / "spec.yml").read_text())
    return next(c for c in spec["checks"] if c["type"] == "pyfunc")


def _run(task: str, fname: str, which: str):
    sub = TASKS / task / which / fname
    ctx = Context(repo_root=REPO, task_dir=TASKS / task, submission_path=sub, db=None)
    return PyFuncCheck(_spec(task)).run(ctx)


def test_registered():
    assert "pyfunc" in REGISTRY


def test_norm_is_recursive_and_number_tolerant():
    assert _norm([{"a": 34}]) == _norm([{"a": 34.0}])
    assert _norm({"x": [1, 2.0]}) == _norm({"x": [1.0, 2]})


@pytest.mark.parametrize("task,fname", ALL_TASKS)
def test_solution_passes(task, fname):
    assert _run(task, fname, "solution").status is Status.PASS


@pytest.mark.parametrize("task,fname", ALL_TASKS)
def test_scaffold_fails(task, fname):
    assert _run(task, fname, "scaffold").status is Status.FAIL


def test_wrong_order_fails():
    # a line series returned out of order must not pass (order matters)
    spec = _spec("revenue-by-day")
    reversed_expect = list(reversed(spec["expect"]))
    got = PyFuncCheck({**spec, "expect": reversed_expect})
    sub = TASKS / "revenue-by-day" / "solution" / "revenue_by_day.py"
    ctx = Context(repo_root=REPO, task_dir=TASKS, submission_path=sub, db=None)
    assert got.run(ctx).status is Status.FAIL
