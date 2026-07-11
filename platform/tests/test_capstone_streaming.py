"""E2E tests for the Stateful Streaming capstone (3 real streaming queries).
Gated on pyspark (needs Java too)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from grader.context import Context
from grader.result import Status

REPO = Path(__file__).resolve().parents[2]
TASK = REPO / "projects/datamart-intelligence-platform/tasks/capstone/stateful-streaming"


def _streaming_checks() -> list[dict]:
    spec = yaml.safe_load((TASK / "spec.yml").read_text())
    return [c for c in spec["checks"] if c["type"] == "spark_streaming"]


def _run(check_spec: dict, which: str):
    from grader.checks.spark_streaming import SparkStreamingCheck
    sub = TASK / which / "streaming_pipeline.py"
    ctx = Context(repo_root=REPO, task_dir=TASK, submission_path=sub, db=None)
    return SparkStreamingCheck(check_spec).run(ctx)


@pytest.mark.parametrize("stage", range(3))
def test_solution_passes_every_stage(stage):
    pytest.importorskip("pyspark")
    res = _run(_streaming_checks()[stage], "solution")
    if res.status is Status.ERROR:
        pytest.skip(f"Spark could not start: {res.hint}")
    assert res.status is Status.PASS, res.hint


@pytest.mark.parametrize("stage", range(3))
def test_scaffold_fails_every_stage(stage):
    pytest.importorskip("pyspark")
    res = _run(_streaming_checks()[stage], "scaffold")
    if res.status is Status.ERROR:
        pytest.skip(f"Spark could not start: {res.hint}")
    assert res.status is Status.FAIL
