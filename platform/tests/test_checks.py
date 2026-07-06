"""Discrimination proof for each check type: pass, fail, and infra-down."""

from __future__ import annotations

from grader.checks.file_check import FileContains, FileExists
from grader.checks.sql_check import SqlAssert
from grader.context import Context, InfraError
from grader.result import Status


class FakeDB:
    def __init__(self, rows=None, exc=None):
        self._rows = rows or []
        self._exc = exc

    def query(self, sql, params=None):
        if self._exc:
            raise self._exc
        return self._rows


def ctx_for(tmp_path, db=None):
    return Context(
        repo_root=tmp_path,
        task_dir=tmp_path,
        submission_path=tmp_path / "sub.sql",
        db=db or FakeDB(),
    )


# ---- file_exists ----
def test_file_exists_pass(tmp_path):
    ctx = ctx_for(tmp_path)
    ctx.submission_path.write_text("SELECT 1;")
    assert FileExists({"type": "file_exists"}).run(ctx).status is Status.PASS


def test_file_exists_fail_when_missing(tmp_path):
    assert FileExists({"type": "file_exists"}).run(ctx_for(tmp_path)).status is Status.FAIL


def test_file_exists_fail_when_empty(tmp_path):
    ctx = ctx_for(tmp_path)
    ctx.submission_path.write_text("")
    assert FileExists({"type": "file_exists"}).run(ctx).status is Status.FAIL


# ---- file_contains ----
def test_file_contains_pass(tmp_path):
    ctx = ctx_for(tmp_path)
    ctx.submission_path.write_text("select * from orders")
    r = FileContains({"type": "file_contains", "pattern": r"(?i)from\s+orders"}).run(ctx)
    assert r.status is Status.PASS


def test_file_contains_fail_uses_hint(tmp_path):
    ctx = ctx_for(tmp_path)
    ctx.submission_path.write_text("select 1")
    r = FileContains(
        {"type": "file_contains", "pattern": r"(?i)from\s+orders", "hint": "use orders"}
    ).run(ctx)
    assert r.status is Status.FAIL
    assert r.hint == "use orders"


# ---- sql_assert: pass / fail / infra-down ----
def test_sql_assert_pass(tmp_path):
    ctx = ctx_for(tmp_path, db=FakeDB(rows=[(5,)]))
    r = SqlAssert({"type": "sql_assert", "query": "select 5", "min": 1}).run(ctx)
    assert r.status is Status.PASS


def test_sql_assert_fail(tmp_path):
    ctx = ctx_for(tmp_path, db=FakeDB(rows=[(0,)]))
    r = SqlAssert({"type": "sql_assert", "query": "select 0", "min": 1}).run(ctx)
    assert r.status is Status.FAIL


def test_sql_assert_infra_down_is_error_not_fail(tmp_path):
    # The critical case: a sleeping Postgres must NOT tell a correct learner
    # they are wrong. It must surface as ERROR.
    ctx = ctx_for(tmp_path, db=FakeDB(exc=InfraError("pg is down")))
    r = SqlAssert({"type": "sql_assert", "query": "select 1", "min": 1}).run(ctx)
    assert r.status is Status.ERROR


def test_sql_assert_equals(tmp_path):
    ctx = ctx_for(tmp_path, db=FakeDB(rows=[("Electronics",)]))
    r = SqlAssert({"type": "sql_assert", "query": "q", "equals": "Electronics"}).run(ctx)
    assert r.status is Status.PASS
