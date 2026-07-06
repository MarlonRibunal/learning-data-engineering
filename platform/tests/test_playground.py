"""Unit tests for the playground helpers that don't require a database.

The DB-backed run_sql path is exercised live against the stack (and in CI's e2e).
"""

from __future__ import annotations

from pathlib import Path

from grader.playground import QueryResult, run_sql


def test_as_records_zips_columns_and_rows():
    r = QueryResult(columns=["status", "revenue"],
                    rows=[("shipped", 870), ("pending", 75)])
    assert r.as_records == [
        {"status": "shipped", "revenue": 870},
        {"status": "pending", "revenue": 75},
    ]


def test_empty_sql_returns_error_without_touching_db(tmp_path: Path):
    # The empty-input guard runs before any connection attempt, so this is safe
    # to call with no stack running.
    for blank in ("", "   ", "\n\t"):
        res = run_sql(tmp_path, blank)
        assert res.error is not None
        assert res.rows == []
