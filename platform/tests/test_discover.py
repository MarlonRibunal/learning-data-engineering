"""Task discovery + curriculum ordering."""

from __future__ import annotations

from grader.core import discover_tasks


def _make(tasks_root, sprint, task):
    d = tasks_root / sprint / task
    d.mkdir(parents=True)
    (d / "spec.yml").write_text("title: T\nsubmission_path: x\nchecks:\n  - type: file_exists\n")


def test_discover_orders_curriculum(tmp_path):
    tasks_root = tmp_path / "tasks"
    # Create out of order on purpose.
    _make(tasks_root, "capstone", "analytics-platform")
    _make(tasks_root, "sprint-3-airflow", "hello-dag")
    _make(tasks_root, "sql-fundamentals", "revenue-by-category")
    _make(tasks_root, "sprint-2-dbt", "revenue-by-status")

    order = [s for s, _ in discover_tasks(tmp_path, tasks_root=tasks_root)]
    # fundamentals first, numbered sprints next, capstone last
    assert order == ["sql-fundamentals", "sprint-2-dbt", "sprint-3-airflow", "capstone"]


def test_discover_empty_when_no_tasks(tmp_path):
    assert discover_tasks(tmp_path, tasks_root=tmp_path / "nope") == []
