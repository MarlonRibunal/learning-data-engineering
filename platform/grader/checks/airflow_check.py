"""Airflow check: trigger a DAG and poll it to completion via the in-container
Airflow CLI (no REST auth needed — we exec into the scheduler container).

    PASS  - the DAG run finished in state 'success'
    FAIL  - the DAG run finished in state 'failed'
    ERROR - could not reach Airflow, or the run did not finish in time
"""

from __future__ import annotations

import json
import time

from ..context import Context, InfraError
from ..registry import CheckType, register
from ..result import CheckResult
from ..stack import compose_exec, looks_like_infra, tail

_TERMINAL = {"success", "failed"}


def latest_state(list_runs_json: str) -> str | None:
    """Return the state of the most recent run from `dags list-runs --output json`."""
    try:
        runs = json.loads(list_runs_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(runs, list) or not runs:
        return None

    def sort_key(run: dict) -> str:
        return str(run.get("logical_date") or run.get("execution_date")
                   or run.get("start_date") or "")

    latest = max(runs, key=sort_key)
    state = latest.get("state")
    return str(state).lower() if state else None


@register("airflow")
class AirflowRun(CheckType):
    """Spec keys:
        dag_id:         the DAG to trigger (required)
        service:        compose service with the Airflow CLI (default "airflow-scheduler")
        poll_attempts:  how many times to poll for completion (default 30)
        poll_interval:  seconds between polls (default 2)
        timeout:        per-command timeout in seconds (default 60)
    """

    def run(self, ctx: Context) -> CheckResult:
        if ctx.runner is None:
            return self._error("no command runner available to reach the stack")

        dag_id = self.spec.get("dag_id")
        if not dag_id:
            return self._fail("task spec error: airflow check needs a 'dag_id'")

        service = self.spec.get("service", "airflow-scheduler")
        timeout = self.spec.get("timeout", 60)
        runner = ctx.runner

        try:
            runner.run(compose_exec(service, "airflow", "dags", "unpause", dag_id), timeout=timeout)
            trig = runner.run(compose_exec(service, "airflow", "dags", "trigger", dag_id), timeout=timeout)
        except InfraError as exc:
            return self._error(str(exc))

        if not trig.ok:
            if looks_like_infra(trig.output):
                return self._error("Airflow unavailable:\n" + tail(trig.output))
            return self._fail("could not trigger the DAG:\n" + tail(trig.output))

        attempts = self.spec.get("poll_attempts", 30)
        interval = self.spec.get("poll_interval", 2)
        for i in range(attempts):
            try:
                res = runner.run(
                    compose_exec(service, "airflow", "dags", "list-runs",
                                 "-d", dag_id, "--output", "json"),
                    timeout=timeout,
                )
            except InfraError as exc:
                return self._error(str(exc))
            if not res.ok and looks_like_infra(res.output):
                return self._error("Airflow unavailable while polling:\n" + tail(res.output))

            state = latest_state(res.stdout)
            if state == "success":
                return self._pass()
            if state == "failed":
                return self._fail(self.spec.get("hint") or f"DAG {dag_id} finished in state 'failed'")
            if i < attempts - 1:
                time.sleep(interval)

        return self._error(f"DAG {dag_id} did not finish within "
                           f"{attempts * interval}s — still running or stuck")
