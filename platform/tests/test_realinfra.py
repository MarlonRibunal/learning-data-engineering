"""Unit tests for the real-infra check types (dbt_test, airflow) and reseed.

They inject a fake command runner and fake DB, so they prove the pass / fail /
infra-down discrimination without a running stack. End-to-end against the real
stack is a separate smoke test (CI / manual).
"""

from __future__ import annotations

import json
import textwrap

import pytest

from grader.checks.airflow_check import AirflowRun, latest_state
from grader.checks.dbt_check import DbtTest
from grader.context import Context, InfraError, RunResult
from grader.core import run_check
from grader.result import Status


class FakeRunner:
    """Routes each `run(args)` through a handler(args) -> RunResult (or raises)."""

    def __init__(self, handler):
        self.handler = handler
        self.calls: list[list[str]] = []

    def run(self, args, timeout=None):
        self.calls.append(list(args))
        return self.handler(args)


class FakeDB:
    def __init__(self, exc=None):
        self.scripts: list[str] = []
        self._exc = exc

    def query(self, sql, params=None):
        return []

    def execute_script(self, sql):
        if self._exc:
            raise self._exc
        self.scripts.append(sql)


def ctx(tmp_path, runner=None, db=None):
    return Context(
        repo_root=tmp_path, task_dir=tmp_path,
        submission_path=tmp_path / "m.sql",
        db=db or FakeDB(), runner=runner,
    )


# ---- dbt_test: pass / fail / infra ----
def test_dbt_pass(tmp_path):
    runner = FakeRunner(lambda args: RunResult(0, "Completed successfully"))
    r = DbtTest({"type": "dbt_test", "select": "m"}).run(ctx(tmp_path, runner))
    assert r.status is Status.PASS
    assert "dbt" in runner.calls[0] and "build" in runner.calls[0]


def test_dbt_fail_on_test_failure(tmp_path):
    runner = FakeRunner(lambda args: RunResult(1, "", "Failure in test not_null_x (1 of 1)"))
    r = DbtTest({"type": "dbt_test", "select": "m"}).run(ctx(tmp_path, runner))
    assert r.status is Status.FAIL


def test_dbt_error_when_service_missing(tmp_path):
    runner = FakeRunner(lambda args: RunResult(1, "", "no such service: dbt-service"))
    r = DbtTest({"type": "dbt_test"}).run(ctx(tmp_path, runner))
    assert r.status is Status.ERROR


def test_dbt_error_when_docker_missing(tmp_path):
    def boom(args):
        raise InfraError("command not found: docker")
    r = DbtTest({"type": "dbt_test"}).run(ctx(tmp_path, FakeRunner(boom)))
    assert r.status is Status.ERROR


def test_dbt_error_when_no_runner(tmp_path):
    r = DbtTest({"type": "dbt_test"}).run(ctx(tmp_path, runner=None))
    assert r.status is Status.ERROR


# ---- airflow: pass / fail / infra / timeout ----
def _airflow_handler(list_runs_result):
    def handler(args):
        if "list-runs" in args:
            return list_runs_result
        return RunResult(0)  # unpause / trigger succeed
    return handler


def test_airflow_pass(tmp_path):
    runs = json.dumps([{"state": "success", "logical_date": "2026-01-02"}])
    runner = FakeRunner(_airflow_handler(RunResult(0, runs)))
    r = AirflowRun({"type": "airflow", "dag_id": "d", "poll_interval": 0}).run(ctx(tmp_path, runner))
    assert r.status is Status.PASS


def test_airflow_fail(tmp_path):
    runs = json.dumps([{"state": "failed", "logical_date": "2026-01-02"}])
    runner = FakeRunner(_airflow_handler(RunResult(0, runs)))
    r = AirflowRun({"type": "airflow", "dag_id": "d", "poll_interval": 0}).run(ctx(tmp_path, runner))
    assert r.status is Status.FAIL


def test_airflow_error_on_trigger_infra(tmp_path):
    def handler(args):
        if "trigger" in args:
            return RunResult(1, "", "Error response from daemon: no such container")
        return RunResult(0)
    r = AirflowRun({"type": "airflow", "dag_id": "d"}).run(ctx(tmp_path, FakeRunner(handler)))
    assert r.status is Status.ERROR


def test_airflow_error_on_timeout(tmp_path):
    runs = json.dumps([{"state": "running", "logical_date": "2026-01-02"}])
    runner = FakeRunner(_airflow_handler(RunResult(0, runs)))
    r = AirflowRun(
        {"type": "airflow", "dag_id": "d", "poll_attempts": 2, "poll_interval": 0}
    ).run(ctx(tmp_path, runner))
    assert r.status is Status.ERROR


def test_airflow_needs_dag_id(tmp_path):
    r = AirflowRun({"type": "airflow"}).run(ctx(tmp_path, FakeRunner(lambda a: RunResult(0))))
    assert r.status is Status.FAIL


# ---- latest_state parsing ----
def test_latest_state_picks_most_recent():
    runs = json.dumps([
        {"state": "failed", "logical_date": "2026-01-01"},
        {"state": "success", "logical_date": "2026-01-03"},
    ])
    assert latest_state(runs) == "success"


def test_latest_state_handles_empty_and_bad():
    assert latest_state("[]") is None
    assert latest_state("not json") is None


# ---- reseed wiring in run_check ----
def _write_reseed_task(tmp_path):
    (tmp_path / "docker-compose.yml").write_text("x")
    tasks_root = tmp_path / "tasks"
    d = tasks_root / "s" / "t"
    d.mkdir(parents=True)
    (tmp_path / "seed.sql").write_text("TRUNCATE raw.orders;")
    (d / "spec.yml").write_text(textwrap.dedent("""
        title: T
        submission_path: submissions/x.sql
        reseed: seed.sql
        checks:
          - type: file_exists
    """))
    (tmp_path / "submissions").mkdir()
    (tmp_path / "submissions" / "x.sql").write_text("SELECT 1;")
    return tmp_path, tasks_root


def test_reseed_runs_before_checks(tmp_path):
    repo, tasks_root = _write_reseed_task(tmp_path)
    db = FakeDB()
    r = run_check("s", "t", repo, tasks_root=tasks_root, db=db, record_progress=False)
    assert r.passed
    assert db.scripts == ["TRUNCATE raw.orders;"]


def test_reseed_failure_is_error(tmp_path):
    repo, tasks_root = _write_reseed_task(tmp_path)
    db = FakeDB(exc=InfraError("pg down"))
    r = run_check("s", "t", repo, tasks_root=tasks_root, db=db, record_progress=False)
    assert r.status is Status.ERROR
    assert r.checks[0].name == "reseed source data"
