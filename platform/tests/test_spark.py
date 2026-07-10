"""Tests for the `spark` check.

The row-comparison logic and registration run everywhere (no pyspark needed).
The end-to-end cases that actually start Spark are skipped unless pyspark is
installed — so the CI unit job (pyyaml + pytest only) stays green, while a
dev box with `pip install pyspark` + Java exercises the real thing.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from grader.checks.spark_check import SparkCheck, _key, _norm, _rows_equal
from grader.context import Context
from grader.registry import REGISTRY
from grader.result import Status

REPO = Path(__file__).resolve().parents[2]
TASKS = REPO / "projects/datamart-intelligence-platform/tasks/sprint-4-spark"


# ---- pure comparison logic (no Spark) ----
def test_spark_check_is_registered():
    assert "spark" in REGISTRY


def test_norm_coerces_numbers():
    assert _norm(100) == _norm(100.0) == _norm(Decimal("100"))
    assert _norm(True) is True  # bools are not treated as ints


def test_rows_equal_unordered():
    got = [{"c": "Books", "r": 20}, {"c": "Home", "r": 60}]
    exp = [{"c": "Home", "r": 60.0}, {"c": "Books", "r": Decimal("20")}]
    assert _rows_equal(got, exp, ordered=False)
    assert not _rows_equal(got, exp, ordered=True)


def test_rows_equal_detects_wrong_and_extra_rows():
    assert not _rows_equal([{"a": 1}], [{"a": 2}], ordered=False)
    assert not _rows_equal([{"a": 1}], [{"a": 1}, {"a": 2}], ordered=False)
    # an extra column is a mismatch (strict on shape)
    assert not _rows_equal([{"a": 1, "b": 2}], [{"a": 1}], ordered=False)


def test_key_is_order_independent_within_a_row():
    assert _key({"a": 1, "b": 2}) == _key({"b": 2, "a": 1})


# ---- end-to-end against a real Spark session (gated per-test) ----
ALL_TASKS = ["select-and-filter", "groupby-agg", "join-orders-customers",
             "partition-cache", "window-rank", "dedupe-latest"]


def _spark_spec(task: str) -> dict:
    spec = yaml.safe_load((TASKS / task / "spec.yml").read_text())
    return next(c for c in spec["checks"] if c["type"] == "spark")


def _run(task: str, which: str):
    """Run the spark check for a task against its scaffold or solution file."""
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


def test_missing_function_fails(tmp_path):
    pytest.importorskip("pyspark")
    sub = tmp_path / "transform.py"
    sub.write_text("x = 1\n")  # no `transform`
    ctx = Context(repo_root=REPO, task_dir=TASKS, submission_path=sub, db=None)
    res = SparkCheck(_spark_spec("groupby-agg")).run(ctx)
    if res.status is Status.ERROR:
        pytest.skip(f"Spark could not start: {res.hint}")
    assert res.status is Status.FAIL
