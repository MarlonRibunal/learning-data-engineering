"""E2E tests for the Incident Response capstone (4 pyfunc stages). Runs in CI."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from grader.checks.pyfunc import PyFuncCheck
from grader.context import Context
from grader.result import Status

REPO = Path(__file__).resolve().parents[2]
TASK = REPO / "projects/datamart-intelligence-platform/tasks/capstone/incident-response"


def _checks() -> list[dict]:
    spec = yaml.safe_load((TASK / "spec.yml").read_text())
    return [c for c in spec["checks"] if c["type"] == "pyfunc"]


def _run(check_spec: dict, which: str):
    sub = TASK / which / "incident_response.py"
    ctx = Context(repo_root=REPO, task_dir=TASK, submission_path=sub, db=None)
    return PyFuncCheck(check_spec).run(ctx)


@pytest.mark.parametrize("stage", range(4))
def test_solution_passes_every_stage(stage):
    assert _run(_checks()[stage], "solution").status is Status.PASS


@pytest.mark.parametrize("stage", range(4))
def test_scaffold_fails_every_stage(stage):
    assert _run(_checks()[stage], "scaffold").status is Status.FAIL
