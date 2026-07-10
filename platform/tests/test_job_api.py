"""Tests for the `job_api` check (hybrid-cloud orchestration).

Pure Python — no Spark, no stack — so these run in the CI unit job.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from grader.checks.job_api import JobApiCheck
from grader.context import Context
from grader.registry import REGISTRY
from grader.result import Status

REPO = Path(__file__).resolve().parents[2]
TASKS = REPO / "projects/datamart-intelligence-platform/tasks/sprint-5-hybrid-cloud"
ALL_TASKS = ["submit-and-poll", "handle-failure"]


def _spec(task: str) -> dict:
    spec = yaml.safe_load((TASKS / task / "spec.yml").read_text())
    return next(c for c in spec["checks"] if c["type"] == "job_api")


def _run(task: str, which: str):
    sub = TASKS / task / which / "run_and_wait.py"
    ctx = Context(repo_root=REPO, task_dir=TASKS / task, submission_path=sub, db=None)
    return JobApiCheck(_spec(task)).run(ctx)


def test_registered():
    assert "job_api" in REGISTRY


@pytest.mark.parametrize("task", ALL_TASKS)
def test_solution_passes(task):
    assert _run(task, "solution").status is Status.PASS


@pytest.mark.parametrize("task", ALL_TASKS)
def test_scaffold_fails(task):
    assert _run(task, "scaffold").status is Status.FAIL


def test_missing_function_fails(tmp_path):
    sub = tmp_path / "run_and_wait.py"
    sub.write_text("x = 1\n")
    ctx = Context(repo_root=REPO, task_dir=TASKS, submission_path=sub, db=None)
    assert JobApiCheck(_spec("submit-and-poll")).run(ctx).status is Status.FAIL
