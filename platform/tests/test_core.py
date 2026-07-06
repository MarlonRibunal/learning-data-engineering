"""Core orchestration: spec loading, dispatch, start, aggregation, progress."""

from __future__ import annotations

import textwrap

import pytest

from grader import progress
from grader.core import run_check, start
from grader.registry import CheckType, build_check, register
from grader.result import CheckResult, Result, Status
from grader.spec import SpecError


def make_repo(tmp_path):
    (tmp_path / "docker-compose.yml").write_text("x")
    tasks_root = tmp_path / "tasks"
    tasks_root.mkdir()
    return tmp_path, tasks_root


def write_task(tasks_root, sprint, task, spec_text):
    d = tasks_root / sprint / task
    d.mkdir(parents=True)
    (d / "spec.yml").write_text(textwrap.dedent(spec_text))
    return d


def test_run_check_pass(tmp_path):
    repo, tasks_root = make_repo(tmp_path)
    write_task(tasks_root, "s1", "t1", """
        title: T
        submission_path: submissions/x.sql
        checks:
          - type: file_contains
            pattern: "(?i)from orders"
    """)
    (repo / "submissions").mkdir()
    (repo / "submissions" / "x.sql").write_text("select * from orders")
    r = run_check("s1", "t1", repo, tasks_root=tasks_root, record_progress=False)
    assert r.passed


def test_run_check_fail(tmp_path):
    repo, tasks_root = make_repo(tmp_path)
    write_task(tasks_root, "s1", "t1", """
        title: T
        submission_path: submissions/x.sql
        checks:
          - type: file_contains
            pattern: "(?i)from orders"
    """)
    (repo / "submissions").mkdir()
    (repo / "submissions" / "x.sql").write_text("select 1")
    r = run_check("s1", "t1", repo, tasks_root=tasks_root, record_progress=False)
    assert r.status is Status.FAIL


def test_missing_spec_raises(tmp_path):
    repo, tasks_root = make_repo(tmp_path)
    with pytest.raises(SpecError):
        run_check("nope", "nope", repo, tasks_root=tasks_root, record_progress=False)


def test_bad_yaml_raises_specerror(tmp_path):
    repo, tasks_root = make_repo(tmp_path)
    d = tasks_root / "s1" / "t1"
    d.mkdir(parents=True)
    (d / "spec.yml").write_text("title: [unclosed\nsubmission_path: x\n")
    with pytest.raises(SpecError):
        run_check("s1", "t1", repo, tasks_root=tasks_root, record_progress=False)


def test_missing_submission_path_raises(tmp_path):
    repo, tasks_root = make_repo(tmp_path)
    write_task(tasks_root, "s1", "t1", """
        title: T
        checks:
          - type: file_exists
    """)
    with pytest.raises(SpecError):
        run_check("s1", "t1", repo, tasks_root=tasks_root, record_progress=False)


def test_unknown_check_type_raises_specerror(tmp_path):
    repo, tasks_root = make_repo(tmp_path)
    write_task(tasks_root, "s1", "t1", """
        title: T
        submission_path: submissions/x.sql
        checks:
          - type: does_not_exist
    """)
    with pytest.raises(SpecError):
        run_check("s1", "t1", repo, tasks_root=tasks_root, record_progress=False)


def test_build_check_unknown_type_raises_keyerror():
    with pytest.raises(KeyError):
        build_check({"type": "does_not_exist"})


def test_build_check_missing_type_raises_keyerror():
    with pytest.raises(KeyError):
        build_check({})


def test_duplicate_registration_raises():
    with pytest.raises(ValueError):
        @register("file_exists")  # already registered
        class _Dup(CheckType):
            pass


def test_result_error_beats_fail():
    r = Result("s", "t", [
        CheckResult("a", Status.PASS),
        CheckResult("b", Status.FAIL),
        CheckResult("c", Status.ERROR),
    ])
    assert r.status is Status.ERROR


def test_start_copies_scaffold(tmp_path):
    repo, tasks_root = make_repo(tmp_path)
    d = write_task(tasks_root, "s1", "t1", """
        title: T
        submission_path: submissions/x.sql
        scaffold: scaffold/x.sql
        checks:
          - type: file_exists
    """)
    (d / "scaffold").mkdir()
    (d / "scaffold" / "x.sql").write_text("-- TODO\n")
    dst = start("s1", "t1", repo, tasks_root=tasks_root)
    assert dst.read_text() == "-- TODO\n"


def test_start_refuses_overwrite(tmp_path):
    repo, tasks_root = make_repo(tmp_path)
    d = write_task(tasks_root, "s1", "t1", """
        title: T
        submission_path: submissions/x.sql
        scaffold: scaffold/x.sql
        checks:
          - type: file_exists
    """)
    (d / "scaffold").mkdir()
    (d / "scaffold" / "x.sql").write_text("-- TODO\n")
    start("s1", "t1", repo, tasks_root=tasks_root)
    with pytest.raises(FileExistsError):
        start("s1", "t1", repo, tasks_root=tasks_root)


def test_progress_records_and_increments(tmp_path):
    repo, _ = make_repo(tmp_path)
    progress.record(repo, "s1", "t1", "fail")
    data = progress.record(repo, "s1", "t1", "pass")
    assert data["s1"]["t1"]["status"] == "pass"
    assert data["s1"]["t1"]["attempts"] == 2
