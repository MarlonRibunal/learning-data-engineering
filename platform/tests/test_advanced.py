"""Tests for the Advanced Challenges sprint (pyfunc). Runs in CI."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from grader.checks.pyfunc import PyFuncCheck
from grader.context import Context
from grader.result import Status

REPO = Path(__file__).resolve().parents[2]
TASKS = REPO / "projects/datamart-intelligence-platform/tasks/sprint-advanced"
ALL_TASKS = [
    ("blast-radius", "blast_radius.py"),
    ("sessionize", "sessionize.py"),
    ("cohort-retention", "retention.py"),
    ("topo-order", "topo_order.py"),
]


def _spec(task: str) -> dict:
    spec = yaml.safe_load((TASKS / task / "spec.yml").read_text())
    return next(c for c in spec["checks"] if c["type"] == "pyfunc")


def _run(task: str, fname: str, which: str):
    sub = TASKS / task / which / fname
    ctx = Context(repo_root=REPO, task_dir=TASKS / task, submission_path=sub, db=None)
    return PyFuncCheck(_spec(task)).run(ctx)


@pytest.mark.parametrize("task,fname", ALL_TASKS)
def test_solution_passes(task, fname):
    assert _run(task, fname, "solution").status is Status.PASS


@pytest.mark.parametrize("task,fname", ALL_TASKS)
def test_scaffold_fails(task, fname):
    assert _run(task, fname, "scaffold").status is Status.FAIL
