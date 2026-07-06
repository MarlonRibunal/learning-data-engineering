"""Tests for the portfolio proof-artifact generator and its wiring."""

from __future__ import annotations

import json
import textwrap

from grader.context import Context
from grader.core import run_check
from grader.proof import generate_proof
from grader.result import CheckResult, Result, Status
from grader.spec import TaskSpec


class FakeDB:
    def __init__(self, rows=None, exc=None):
        self._rows = rows or []
        self._exc = exc

    def query(self, sql, params=None):
        if self._exc:
            raise self._exc
        return self._rows

    def execute_script(self, sql):
        pass


def _spec(tmp_path, proof):
    return TaskSpec(
        sprint="capstone", task="analytics-platform", task_dir=tmp_path,
        title="Capstone", submission_path="submissions/x.sql",
        checks=[], proof=proof,
    )


def _ctx(tmp_path, db):
    return Context(repo_root=tmp_path, task_dir=tmp_path,
                   submission_path=tmp_path / "x.sql", db=db, runner=None)


def test_generate_proof_writes_files(tmp_path):
    proof = {"title": "My Platform", "summary": "did a thing",
             "pipeline": "raw --> mart --> dag"}
    result = Result("capstone", "analytics-platform", [
        CheckResult("model builds", Status.PASS),
        CheckResult("dag runs", Status.PASS),
    ])
    out_dir = generate_proof("capstone", "analytics-platform",
                             _spec(tmp_path, proof), result, _ctx(tmp_path, FakeDB()), tmp_path)

    md = (out_dir / "PORTFOLIO.md").read_text()
    assert "My Platform" in md
    assert "model builds" in md and "dag runs" in md
    assert "raw --> mart --> dag" in md

    data = json.loads((out_dir / "verified-checks.json").read_text())
    assert data["title"] == "My Platform"
    assert [c["name"] for c in data["checks"]] == ["model builds", "dag runs"]
    assert data["status"] == "pass"


def test_generate_proof_chart_falls_back_to_table(tmp_path):
    # With rows but (likely) no matplotlib, the md should carry a data table.
    proof = {"title": "P", "chart": {"query": "select status, revenue from t"}}
    result = Result("c", "t", [CheckResult("ok", Status.PASS)])
    db = FakeDB(rows=[("shipped", 870.0), ("pending", 75.0)])
    out_dir = generate_proof("c", "t", _spec(tmp_path, proof), result,
                             _ctx(tmp_path, db), tmp_path)
    md = (out_dir / "PORTFOLIO.md").read_text()
    # Either an embedded chart image or a rendered table — but the data is present.
    assert "chart.png" in md or "shipped" in md


def test_generate_proof_survives_db_down(tmp_path):
    proof = {"title": "P", "chart": {"query": "select 1"}}
    result = Result("c", "t", [CheckResult("ok", Status.PASS)])
    db = FakeDB(exc=RuntimeError("db down"))
    # Must not raise — proof is best-effort.
    out_dir = generate_proof("c", "t", _spec(tmp_path, proof), result,
                             _ctx(tmp_path, db), tmp_path)
    assert (out_dir / "PORTFOLIO.md").is_file()


def _write_proof_task(tmp_path, submission_text):
    (tmp_path / "docker-compose.yml").write_text("x")
    tasks_root = tmp_path / "tasks"
    d = tasks_root / "cap" / "t"
    d.mkdir(parents=True)
    (d / "spec.yml").write_text(textwrap.dedent("""
        title: Cap
        submission_path: submissions/x.sql
        checks:
          - type: file_contains
            pattern: "(?i)from orders"
        proof:
          title: Cap Proof
          summary: built it
    """))
    (tmp_path / "submissions").mkdir()
    (tmp_path / "submissions" / "x.sql").write_text(submission_text)
    return tmp_path, tasks_root


def test_run_check_emits_proof_on_pass(tmp_path):
    repo, tasks_root = _write_proof_task(tmp_path, "select * from orders")
    r = run_check("cap", "t", repo, tasks_root=tasks_root,
                  db=FakeDB(), record_progress=False, make_proof=True)
    assert r.passed
    assert r.proof_dir is not None
    assert (r.proof_dir / "PORTFOLIO.md").is_file()
    assert (r.proof_dir / "verified-checks.json").is_file()


def test_run_check_no_proof_on_fail(tmp_path):
    repo, tasks_root = _write_proof_task(tmp_path, "select 1")
    r = run_check("cap", "t", repo, tasks_root=tasks_root,
                  db=FakeDB(), record_progress=False, make_proof=True)
    assert r.status is Status.FAIL
    assert r.proof_dir is None


def test_run_check_no_proof_when_not_requested(tmp_path):
    repo, tasks_root = _write_proof_task(tmp_path, "select * from orders")
    r = run_check("cap", "t", repo, tasks_root=tasks_root,
                  db=FakeDB(), record_progress=False, make_proof=False)
    assert r.passed
    assert r.proof_dir is None
