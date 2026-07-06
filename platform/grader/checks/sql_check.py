"""SQL data-contract check.

Runs a query against Postgres and asserts on the result. Used for data-contract
checks the learner's work must satisfy (row counts, uniqueness, value ranges).
If Postgres is unreachable, the check reports ERROR (not FAIL) — never tell a
correct learner they're wrong because the stack was down.
"""

from __future__ import annotations

from ..context import Context, InfraError
from ..registry import CheckType, register
from ..result import CheckResult


@register("sql_assert")
class SqlAssert(CheckType):
    """Run a query and assert on the first returned scalar.

    Spec keys (query required; at least one assertion required):
        query:      SQL returning a single row/column (required)
        equals:     assert the scalar equals this
        min:        assert the scalar is >= this
        max:        assert the scalar is <= this
        hint:       custom failure message (optional)
    """

    def run(self, ctx: Context) -> CheckResult:
        query = self.spec.get("query")
        if not query:
            return self._fail("task spec error: sql_assert needs a 'query'")

        assertions = {k: self.spec[k] for k in ("equals", "min", "max") if k in self.spec}
        if not assertions:
            return self._fail("task spec error: sql_assert needs equals/min/max")

        try:
            rows = ctx.db.query(query)
        except InfraError as exc:
            return self._error(f"could not run SQL check: {exc}")

        if not rows or not rows[0]:
            return self._fail(f"query returned no rows: {query}")
        actual = rows[0][0]

        hint = self.spec.get("hint")
        if "equals" in assertions and actual != assertions["equals"]:
            return self._fail(hint or f"expected {assertions['equals']}, got {actual}")
        if "min" in assertions and actual < assertions["min"]:
            return self._fail(hint or f"expected >= {assertions['min']}, got {actual}")
        if "max" in assertions and actual > assertions["max"]:
            return self._fail(hint or f"expected <= {assertions['max']}, got {actual}")
        return self._pass()
