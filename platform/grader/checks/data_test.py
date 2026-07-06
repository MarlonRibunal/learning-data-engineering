"""Data-quality check: prove the learner's test actually catches bad data.

A data test (dbt-style) is a query that returns the rows that VIOLATE a rule — it
passes when it returns zero rows. Writing one is easy; writing one that actually
works is the skill. So we run the learner's test against two datasets:

  * clean data  → it must return 0 rows   (no false alarms on good data)
  * dirty data  → it must return >0 rows  (it catches the injected problem)

Only a test that discriminates both ways passes.
"""

from __future__ import annotations

from ..context import Context, InfraError
from ..registry import CheckType, register
from ..result import CheckResult


@register("data_test")
class DataTest(CheckType):
    """Spec keys:
        clean_seed: SQL that loads known-good data (repo-root relative)
        dirty_seed: SQL that injects a violating row into the clean data
        hint:       custom message when the test fails to catch the bad data
    """

    def run(self, ctx: Context) -> CheckResult:
        from ..playground import run_sql

        test_sql = ctx.submission_path.read_text()
        clean = ctx.repo_root / self.spec.get("clean_seed", "")
        dirty = ctx.repo_root / self.spec.get("dirty_seed", "")
        if not clean.is_file() or not dirty.is_file():
            return self._error("task authoring error: clean_seed/dirty_seed not found")

        try:
            ctx.db.execute_script(clean.read_text())
            on_clean = run_sql(ctx.repo_root, test_sql, seed=False)
            ctx.db.execute_script(dirty.read_text())
            on_dirty = run_sql(ctx.repo_root, test_sql, seed=False)
        except InfraError as exc:
            return self._error(f"could not run — the stack looks unavailable ({exc}). "
                               "Start it: ./platform.sh up")

        if on_clean.error or on_dirty.error:
            return self._fail(f"your test query errored: {on_clean.error or on_dirty.error}")
        if on_clean.rows:
            return self._fail("your test flagged GOOD data — a data test should return "
                              "zero rows when everything is fine (it returns the "
                              "*violating* rows).")
        if not on_dirty.rows:
            return self._fail(self.spec.get("hint") or
                              "your test didn't CATCH the bad data — it should return the "
                              "offending rows when the rule is violated.")
        return self._pass()
