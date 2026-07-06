"""Regression proof for the shipped example task.

The solution must pass; the scaffold stub must fail. This is what stops the
grader from silently always-passing, and it verifies the scaffold/solution
split (the learner edits a stub, not the answer).
"""

from __future__ import annotations

from pathlib import Path

from grader.core import run_check
from grader.result import Status

REPO_ROOT = Path(__file__).resolve().parents[2]
TASKS_ROOT = REPO_ROOT / "projects" / "datamart-intelligence-platform" / "tasks"
TASK_DIR = TASKS_ROOT / "sql-fundamentals" / "revenue-by-category"


def _run_with_submission(tmp_path, content: str):
    (tmp_path / "docker-compose.yml").write_text("x")
    sub = tmp_path / "submissions" / "sql-fundamentals" / "revenue_by_category.sql"
    sub.parent.mkdir(parents=True)
    sub.write_text(content)
    return run_check(
        "sql-fundamentals", "revenue-by-category", tmp_path,
        tasks_root=TASKS_ROOT, record_progress=False,
    )


def test_solution_passes(tmp_path):
    solution = (TASK_DIR / "solution" / "revenue_by_category.sql").read_text()
    result = _run_with_submission(tmp_path, solution)
    assert result.passed, [(c.name, c.status.value, c.hint) for c in result.checks]


def test_scaffold_fails(tmp_path):
    scaffold = (TASK_DIR / "scaffold" / "revenue_by_category.sql").read_text()
    result = _run_with_submission(tmp_path, scaffold)
    assert result.status is Status.FAIL
