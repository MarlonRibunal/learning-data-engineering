"""dbt check: run `dbt build` (which runs models AND their tests) in the
dbt-service container and grade the result.

    PASS  - dbt build succeeded (models materialized, tests green)
    FAIL  - dbt ran but models/tests failed (the learner's work is wrong)
    ERROR - dbt could not run at all (stack down, service missing)
"""

from __future__ import annotations

from ..context import Context, InfraError
from ..registry import CheckType, register
from ..result import CheckResult
from ..stack import compose_exec, looks_like_infra, tail


@register("dbt_test")
class DbtTest(CheckType):
    """Spec keys:
        select:   a dbt node selection (e.g. "stg_orders" or "staging"); optional
        service:  compose service to exec into (default "dbt-service")
        timeout:  seconds before the run is treated as hung (default 300)
        hint:     custom failure message (optional)
    """

    def run(self, ctx: Context) -> CheckResult:
        if ctx.runner is None:
            return self._error("no command runner available to reach the stack")

        service = self.spec.get("service", "dbt-service")
        args = compose_exec(service, "dbt", "build")
        select = self.spec.get("select")
        if select:
            args += ["--select", str(select)]

        try:
            res = ctx.runner.run(args, timeout=self.spec.get("timeout", 300))
        except InfraError as exc:
            return self._error(str(exc))

        if res.ok:
            return self._pass()
        if looks_like_infra(res.output):
            return self._error(
                "dbt could not run — the stack looks unavailable. "
                "Start it with `docker compose up -d`.\n" + tail(res.output)
            )
        hint = self.spec.get("hint")
        return self._fail((hint + "\n" if hint else "dbt build/test failed:\n") + tail(res.output))
