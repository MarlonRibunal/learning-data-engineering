"""Unit tests for the sql_ingest check (fake DB, no stack)."""

from __future__ import annotations

from grader.checks.sql_ingest import SqlIngest
from grader.context import Context, QueryError
from grader.result import Status


class FakeDB:
    def __init__(self, scalar=3, write_raises_on=None):
        self.scalar = scalar
        self.writes = 0
        self.write_raises_on = write_raises_on

    def run_write(self, sql):
        self.writes += 1
        if self.write_raises_on and self.writes >= self.write_raises_on:
            raise QueryError("duplicate key value violates unique constraint")

    def query(self, sql, params=None):
        return [(self.scalar,)]


def _ctx(tmp_path, db):
    f = tmp_path / "load.sql"
    f.write_text("INSERT INTO raw.products ...")
    return Context(repo_root=tmp_path, task_dir=tmp_path, submission_path=f, db=db)


def test_ingest_pass(tmp_path):
    spec = {"type": "sql_ingest", "asserts": [{"query": "q", "equals": 3}]}
    assert SqlIngest(spec).run(_ctx(tmp_path, FakeDB(scalar=3))).status is Status.PASS


def test_ingest_fail_on_wrong_result(tmp_path):
    spec = {"type": "sql_ingest", "asserts": [{"query": "q", "equals": 3}]}
    assert SqlIngest(spec).run(_ctx(tmp_path, FakeDB(scalar=1))).status is Status.FAIL


def test_ingest_fail_on_sql_error(tmp_path):
    spec = {"type": "sql_ingest", "asserts": []}
    assert SqlIngest(spec).run(_ctx(tmp_path, FakeDB(write_raises_on=1))).status is Status.FAIL


def test_ingest_idempotency_second_run_fails(tmp_path):
    spec = {"type": "sql_ingest", "runs": 2, "asserts": []}
    db = FakeDB(write_raises_on=2)  # first run ok, second raises (not idempotent)
    result = SqlIngest(spec).run(_ctx(tmp_path, db))
    assert result.status is Status.FAIL
    assert db.writes == 2
    assert "idempotent" in result.hint
