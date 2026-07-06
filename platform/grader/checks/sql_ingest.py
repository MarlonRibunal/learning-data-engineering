"""Ingestion check: run the learner's load SQL, then assert on the target table.

Ingestion is "getting data in" — the learner writes SQL that lands/loads source
data into a target table. This check runs that SQL (optionally twice, to prove the
load is idempotent) and then verifies the result with assertion queries.

    PASS  - the load ran and the target table matches
    FAIL  - the learner's SQL errored, or the loaded data is wrong
    ERROR - the stack was unavailable
"""

from __future__ import annotations

from ..context import Context, InfraError, QueryError
from ..registry import CheckType, register
from ..result import CheckResult


@register("sql_ingest")
class SqlIngest(CheckType):
    """Spec keys:
        runs:    how many times to run the learner's SQL (2 proves idempotency)
        asserts: list of {query, equals|min|max, hint} run after the load
    """

    def run(self, ctx: Context) -> CheckResult:
        learner_sql = ctx.submission_path.read_text()
        runs = int(self.spec.get("runs", 1))

        try:
            for _ in range(runs):
                ctx.db.run_write(learner_sql)
        except QueryError as exc:
            extra = " (it worked once but failed when run again — make it idempotent)" \
                if runs > 1 else ""
            return self._fail(f"your SQL errored{extra}: {exc}")
        except InfraError as exc:
            return self._error(f"could not run — the stack looks unavailable ({exc}). "
                               "Start it: ./platform.sh up")

        for assertion in self.spec.get("asserts", []):
            outcome = self._check_assertion(ctx, assertion)
            if outcome is not None:
                return outcome
        return self._pass()

    def _check_assertion(self, ctx: Context, assertion: dict) -> CheckResult | None:
        query = assertion.get("query")
        if not query:
            return self._fail("task spec error: an assert is missing its 'query'")
        try:
            rows = ctx.db.query(query)
        except InfraError as exc:
            return self._error(str(exc))
        actual = rows[0][0] if rows and rows[0] else None
        hint = assertion.get("hint")
        if "equals" in assertion and actual != assertion["equals"]:
            return self._fail(hint or f"expected {assertion['equals']}, got {actual}")
        if "min" in assertion and (actual is None or actual < assertion["min"]):
            return self._fail(hint or f"expected >= {assertion['min']}, got {actual}")
        if "max" in assertion and (actual is None or actual > assertion["max"]):
            return self._fail(hint or f"expected <= {assertion['max']}, got {actual}")
        return None
