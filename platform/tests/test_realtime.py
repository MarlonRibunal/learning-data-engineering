"""End-to-end tests for the real-time windowing sprint.

These reuse the `spark` check, so they need a real Spark session — gated on
`pytest.importorskip("pyspark")` so the CI unit job (no pyspark) stays green.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from grader.checks.spark_check import SparkCheck
from grader.context import Context
from grader.result import Status

REPO = Path(__file__).resolve().parents[2]
TASKS = REPO / "projects/datamart-intelligence-platform/tasks/sprint-8-realtime"
ALL_TASKS = ["tumbling-window-count", "windowed-revenue", "sliding-window-count",
             "windowed-by-category", "distinct-per-window", "session-window"]


def _spark_spec(task: str) -> dict:
    spec = yaml.safe_load((TASKS / task / "spec.yml").read_text())
    return next(c for c in spec["checks"] if c["type"] == "spark")


def _run(task: str, which: str):
    sub = TASKS / task / which / "transform.py"
    ctx = Context(repo_root=REPO, task_dir=TASKS / task, submission_path=sub, db=None)
    return SparkCheck(_spark_spec(task)).run(ctx)


@pytest.mark.parametrize("task", ALL_TASKS)
def test_solution_passes(task):
    pytest.importorskip("pyspark")
    res = _run(task, "solution")
    if res.status is Status.ERROR:
        pytest.skip(f"Spark could not start: {res.hint}")
    assert res.status is Status.PASS, res.hint


@pytest.mark.parametrize("task", ALL_TASKS)
def test_scaffold_fails(task):
    pytest.importorskip("pyspark")
    res = _run(task, "scaffold")
    if res.status is Status.ERROR:
        pytest.skip(f"Spark could not start: {res.hint}")
    assert res.status is Status.FAIL, f"{task} scaffold unexpectedly {res.status}"
