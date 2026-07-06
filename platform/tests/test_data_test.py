"""Unit tests for the data_test check (run_sql monkeypatched — no stack)."""

from __future__ import annotations

import grader.playground as playground
from grader.checks.data_test import DataTest
from grader.context import Context
from grader.playground import QueryResult
from grader.result import Status


class FakeDB:
    def execute_script(self, sql):
        pass

    def query(self, sql, params=None):
        return []


def _ctx(tmp_path):
    (tmp_path / "clean.sql").write_text("-- clean")
    (tmp_path / "dirty.sql").write_text("-- dirty")
    sub = tmp_path / "test.sql"
    sub.write_text("SELECT * FROM orders WHERE ...")
    return Context(repo_root=tmp_path, task_dir=tmp_path, submission_path=sub, db=FakeDB())


def _spec():
    return {"type": "data_test", "clean_seed": "clean.sql", "dirty_seed": "dirty.sql"}


def test_good_test_passes(tmp_path, monkeypatch):
    calls = {"n": 0}

    def fake_run_sql(repo, sql, seed=True):
        calls["n"] += 1
        # 1st call = clean → 0 rows; 2nd = dirty → catches a row
        return QueryResult(rows=[] if calls["n"] == 1 else [(9999,)])

    monkeypatch.setattr(playground, "run_sql", fake_run_sql)
    assert DataTest(_spec()).run(_ctx(tmp_path)).status is Status.PASS


def test_false_alarm_on_clean_fails(tmp_path, monkeypatch):
    # A test that returns rows on clean data is a false alarm.
    monkeypatch.setattr(playground, "run_sql", lambda *a, **k: QueryResult(rows=[(1,)]))
    assert DataTest(_spec()).run(_ctx(tmp_path)).status is Status.FAIL


def test_misses_bad_data_fails(tmp_path, monkeypatch):
    # A test that never returns rows never catches anything.
    monkeypatch.setattr(playground, "run_sql", lambda *a, **k: QueryResult(rows=[]))
    assert DataTest(_spec()).run(_ctx(tmp_path)).status is Status.FAIL


def test_learner_sql_error_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(playground, "run_sql",
                        lambda *a, **k: QueryResult(error="syntax error"))
    assert DataTest(_spec()).run(_ctx(tmp_path)).status is Status.FAIL
