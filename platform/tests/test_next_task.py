"""next_task: the first unpassed task in curriculum order."""

from __future__ import annotations

from grader import progress
from grader.core import next_task


def _make(tasks_root, sprint, task):
    d = tasks_root / sprint / task
    d.mkdir(parents=True)
    (d / "spec.yml").write_text("title: T\nsubmission_path: x\nchecks:\n  - type: file_exists\n")


def _repo(tmp_path):
    (tmp_path / "docker-compose.yml").write_text("x")
    tasks_root = tmp_path / "tasks"
    _make(tasks_root, "sql-fundamentals", "a")
    _make(tasks_root, "sprint-2-dbt", "b")
    _make(tasks_root, "capstone", "c")
    return tmp_path, tasks_root


def test_next_task_is_first_unpassed_in_order(tmp_path):
    repo, tasks_root = _repo(tmp_path)
    # Pass the first; next should be the second, not the capstone.
    progress.record(repo, "sql-fundamentals", "a", "pass")
    assert next_task(repo, tasks_root) == ("sprint-2-dbt", "b")


def test_next_task_skips_passed_but_returns_earlier_unpassed(tmp_path):
    repo, tasks_root = _repo(tmp_path)
    # Only the capstone passed; the earliest unpassed is still first.
    progress.record(repo, "capstone", "c", "pass")
    assert next_task(repo, tasks_root) == ("sql-fundamentals", "a")


def test_next_task_none_when_all_passed(tmp_path):
    repo, tasks_root = _repo(tmp_path)
    for s, t in [("sql-fundamentals", "a"), ("sprint-2-dbt", "b"), ("capstone", "c")]:
        progress.record(repo, s, t, "pass")
    assert next_task(repo, tasks_root) is None
