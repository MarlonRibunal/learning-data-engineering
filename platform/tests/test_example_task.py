"""Regression proof for a shipped SQL task, graded by result-correctness.

Now that SQL tasks grade against the real warehouse, this needs Postgres — so it
SKIPS when the stack isn't running (keeping the no-DB `unit` CI job green) and
runs opportunistically when a stack is available (and in CI's `e2e` job).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from grader.core import run_check
from grader.result import Status

REPO_ROOT = Path(__file__).resolve().parents[2]
TASKS_ROOT = REPO_ROOT / "projects" / "datamart-intelligence-platform" / "tasks"
TASK_DIR = TASKS_ROOT / "sql-fundamentals" / "revenue-by-category"


def _db_available() -> bool:
    try:
        import psycopg2

        from grader.context import _dsn_from_env

        psycopg2.connect(**_dsn_from_env()).close()
        return True
    except Exception:  # noqa: BLE001 - missing driver or unreachable stack
        return False


pytestmark = pytest.mark.skipif(not _db_available(), reason="Postgres stack not running")


def _run(content: str):
    submission = REPO_ROOT / "submissions" / "sql-fundamentals" / "revenue_by_category.sql"
    submission.parent.mkdir(parents=True, exist_ok=True)
    submission.write_text(content)
    try:
        return run_check("sql-fundamentals", "revenue-by-category", REPO_ROOT,
                         tasks_root=TASKS_ROOT, record_progress=False)
    finally:
        submission.unlink(missing_ok=True)


def test_solution_passes():
    result = _run((TASK_DIR / "solution" / "revenue_by_category.sql").read_text())
    assert result.passed, [(c.name, c.status.value, c.hint) for c in result.checks]


def test_scaffold_fails():
    result = _run((TASK_DIR / "scaffold" / "revenue_by_category.sql").read_text())
    assert result.status is Status.FAIL
