"""E2E tests for the Real-Time Monitor capstone (3 Spark stages). Gated on pyspark."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from grader.checks.spark_check import SparkCheck
from grader.context import Context
from grader.result import Status

REPO = Path(__file__).resolve().parents[2]
TASK = REPO / "projects/datamart-intelligence-platform/tasks/capstone/realtime-monitor"


def _spark_checks() -> list[dict]:
    spec = yaml.safe_load((TASK / "spec.yml").read_text())
    return [c for c in spec["checks"] if c["type"] == "spark"]


def _run(check_spec: dict, which: str):
    sub = TASK / which / "realtime_pipeline.py"
    ctx = Context(repo_root=REPO, task_dir=TASK, submission_path=sub, db=None)
    return SparkCheck(check_spec).run(ctx)


@pytest.mark.parametrize("stage", range(3))
def test_solution_passes_every_stage(stage):
    pytest.importorskip("pyspark")
    res = _run(_spark_checks()[stage], "solution")
    if res.status is Status.ERROR:
        pytest.skip(f"Spark could not start: {res.hint}")
    assert res.status is Status.PASS, res.hint


@pytest.mark.parametrize("stage", range(3))
def test_scaffold_fails_every_stage(stage):
    pytest.importorskip("pyspark")
    res = _run(_spark_checks()[stage], "scaffold")
    if res.status is Status.ERROR:
        pytest.skip(f"Spark could not start: {res.hint}")
    assert res.status is Status.FAIL
