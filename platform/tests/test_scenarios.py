"""Tests for the Phase-2 scenario tracks (on-call, debug, migration). In CI."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from grader.checks.pyfunc import PyFuncCheck
from grader.context import Context
from grader.result import Status

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "projects/datamart-intelligence-platform/tasks"

# (sprint, task, submission filename)
ALL_TASKS = [
    ("sprint-oncall", "triage-alerts", "triage.py"),
    ("sprint-oncall", "find-root-cause", "root_cause.py"),
    ("sprint-oncall", "backfill-window", "backfill.py"),
    ("sprint-oncall", "verify-recovery", "verify.py"),
    ("sprint-debug", "fix-the-dedup", "dedupe_latest.py"),
    ("sprint-debug", "fix-the-revenue", "net_revenue.py"),
    ("sprint-debug", "fix-the-rate", "conversion_rate.py"),
    ("sprint-migration", "rename-columns", "rename_keys.py"),
    ("sprint-migration", "backfill-default", "add_column.py"),
    ("sprint-migration", "reconcile-counts", "reconcile.py"),
]


def _spec(sprint: str, task: str) -> dict:
    spec = yaml.safe_load((ROOT / sprint / task / "spec.yml").read_text())
    return next(c for c in spec["checks"] if c["type"] == "pyfunc")


def _run(sprint: str, task: str, fname: str, which: str):
    sub = ROOT / sprint / task / which / fname
    ctx = Context(repo_root=REPO, task_dir=ROOT / sprint / task, submission_path=sub, db=None)
    return PyFuncCheck(_spec(sprint, task)).run(ctx)


@pytest.mark.parametrize("sprint,task,fname", ALL_TASKS)
def test_solution_passes(sprint, task, fname):
    assert _run(sprint, task, fname, "solution").status is Status.PASS


@pytest.mark.parametrize("sprint,task,fname", ALL_TASKS)
def test_scaffold_fails(sprint, task, fname):
    assert _run(sprint, task, fname, "scaffold").status is Status.FAIL
