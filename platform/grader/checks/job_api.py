"""Hybrid-cloud check: grade a learner's external-job orchestrator.

The local stand-in for "Airflow triggers a Databricks job." The learner writes
a function that submits a job to a client, polls its status until the run
finishes, returns the result on success, and raises on failure — the exact
pattern a DatabricksOperator (or any external-job operator) implements.

The grader injects a scripted fake client, so it's fully local and
deterministic — no cloud, no network.

    entry: str    function name, called as entry(client, job_id) (default run_and_wait)
    mode: str     "success" (only the happy path) | "both" (also require it to
                  raise on a FAILED run). Default "success".

    PASS  - returns the job result on success (after polling) and, for mode
            "both", raises on a failed run
    FAIL  - wrong return, didn't poll to completion, or didn't raise on failure
"""

from __future__ import annotations

import importlib.util

from ..context import Context
from ..registry import CheckType, register
from ..result import CheckResult

SUCCESS_RESULT = 42  # what get_result returns on a successful run


def _load_fn(path, name):
    spec = importlib.util.spec_from_file_location("job_submission", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # bad learner code raises — caller catches
    return getattr(mod, name, None)


class _FakeClient:
    """A scripted Databricks-like job client. Returns each status in order,
    then stays on the last one so a correct poll loop always terminates."""

    def __init__(self, statuses):
        self._statuses = list(statuses)
        self._i = 0
        self.submitted = None
        self.poll_count = 0

    def submit(self, job_id):
        self.submitted = job_id
        return "run-1"

    def get_status(self, run_id):
        self.poll_count += 1
        if self.poll_count > 1000:  # break a runaway learner loop
            raise RuntimeError("polled too many times without stopping")
        status = self._statuses[min(self._i, len(self._statuses) - 1)]
        self._i += 1
        return status

    def get_result(self, run_id):
        return SUCCESS_RESULT


@register("job_api")
class JobApiCheck(CheckType):
    def run(self, ctx: Context) -> CheckResult:
        entry = self.spec.get("entry", "run_and_wait")
        mode = self.spec.get("mode", "success")

        try:
            fn = _load_fn(ctx.submission_path, entry)
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"your code failed to import: {exc}")
        if fn is None:
            return self._fail(f"define a function named `{entry}(client, job_id)`")

        # Happy path: RUNNING, RUNNING, then SUCCESS.
        client = _FakeClient(["RUNNING", "RUNNING", "SUCCESS"])
        try:
            got = fn(client, "etl-job")
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"your function raised on a successful job: {exc}")
        if client.submitted != "etl-job":
            return self._fail("submit the job with client.submit(job_id) first")
        if client.poll_count < 3:
            return self._fail(
                "poll client.get_status(run_id) until the run finishes — it "
                "wasn't done on the first check (status was RUNNING)"
            )
        if got != SUCCESS_RESULT:
            return self._fail(
                "return the job's result from client.get_result(run_id) on success"
            )

        # Failure path: the run ends FAILED — the orchestrator must raise.
        if mode == "both":
            failed = _FakeClient(["RUNNING", "FAILED"])
            try:
                fn(failed, "etl-job")
            except Exception:  # noqa: BLE001 - raising is the correct behavior
                pass
            else:
                return self._fail(
                    "raise an error when the run's status is FAILED (don't return "
                    "as if it succeeded)"
                )

        return self._pass()
