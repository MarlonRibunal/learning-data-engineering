"""Tests for the `spark_streaming` check. Registration runs in CI; the real
streaming run is gated on pyspark (needs Java too)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from grader.registry import REGISTRY
from grader.result import Status

REPO = Path(__file__).resolve().parents[2]
TASK = REPO / "projects/datamart-intelligence-platform/tasks/sprint-8-realtime/structured-streaming"


def test_spark_streaming_registered():
    import grader.checks  # noqa: F401 - registers check types
    assert "spark_streaming" in REGISTRY


def _spec() -> dict:
    spec = yaml.safe_load((TASK / "spec.yml").read_text())
    return next(c for c in spec["checks"] if c["type"] == "spark_streaming")


def _run(which: str):
    from grader.checks.spark_streaming import SparkStreamingCheck
    from grader.context import Context
    sub = TASK / which / "transform.py"
    ctx = Context(repo_root=REPO, task_dir=TASK, submission_path=sub, db=None)
    return SparkStreamingCheck(_spec()).run(ctx)


def test_solution_passes():
    pytest.importorskip("pyspark")
    res = _run("solution")
    if res.status is Status.ERROR:
        pytest.skip(f"Spark could not start: {res.hint}")
    assert res.status is Status.PASS, res.hint


def test_scaffold_fails():
    pytest.importorskip("pyspark")
    res = _run("scaffold")
    if res.status is Status.ERROR:
        pytest.skip(f"Spark could not start: {res.hint}")
    assert res.status is Status.FAIL
