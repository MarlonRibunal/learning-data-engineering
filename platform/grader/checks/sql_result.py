"""Result-correctness check for plain-SQL tasks.

Instead of pattern-matching the query text, this runs the learner's SQL AND the
reference solution against the seeded warehouse and compares the rows they return.
It grades what the query actually *does*, so a query that "looks right" but returns
the wrong data fails — and a correct query written differently still passes.
"""

from __future__ import annotations

from decimal import Decimal

from ..context import Context, InfraError
from ..registry import CheckType, register
from ..result import CheckResult


def _norm(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, Decimal)):
        return round(float(value), 6)
    return value


def _norm_rows(rows) -> list[tuple]:
    return [tuple(_norm(v) for v in row) for row in rows]


def rows_match(expected, actual, ordered: bool) -> bool:
    exp, act = _norm_rows(expected), _norm_rows(actual)
    if ordered:
        return exp == act
    key = lambda t: tuple(str(v) for v in t)  # noqa: E731 - stable sort across types
    return sorted(exp, key=key) == sorted(act, key=key)


@register("sql_result")
class SqlResult(CheckType):
    """Spec keys:
        ordered: bool  — require the row ORDER to match too (for ORDER BY tasks)
        hint:    str   — custom failure message
    """

    def run(self, ctx: Context) -> CheckResult:
        from ..playground import run_sql

        if ctx.solution_path is None or not ctx.solution_path.is_file():
            return self._error("task authoring error: no solution to compare against")

        learner_sql = ctx.submission_path.read_text()
        solution_sql = ctx.solution_path.read_text()

        try:
            expected = run_sql(ctx.repo_root, solution_sql, seed=True)
            actual = run_sql(ctx.repo_root, learner_sql, seed=False)
        except InfraError as exc:
            return self._error(f"could not run — the stack looks unavailable ({exc}). "
                               "Start it: ./platform.sh up")

        if expected.error:
            return self._error(f"the reference solution failed to run: {expected.error}")
        if actual.error:
            return self._fail(f"your query errored — {actual.error}")

        ordered = bool(self.spec.get("ordered", False))
        if rows_match(expected.rows, actual.rows, ordered):
            return self._pass()

        hint = self.spec.get("hint")
        if hint:
            return self._fail(hint)
        if len(actual.rows) != len(expected.rows):
            return self._fail(f"expected {len(expected.rows)} row(s), your query returned "
                              f"{len(actual.rows)} — check your logic")
        detail = " (and the order)" if ordered else ""
        return self._fail(f"your rows don't match the expected result{detail} — "
                          "run your query to compare")
