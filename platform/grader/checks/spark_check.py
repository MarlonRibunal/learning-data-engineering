"""Big-data check: grade a learner's PySpark transform.

Fully local — a Spark ``local[*]`` session on the host, no cluster, no cloud.
The learner writes a function that takes one or more Spark DataFrames and
returns a transformed DataFrame; the grader builds known inputs, runs the
function, and compares the collected rows to the expected output.

    PASS  - the returned rows match the expected output
    FAIL  - the learner's code errored, returned a non-DataFrame, or the rows
            (or partition count) are wrong
    ERROR - Spark can't run here (pyspark missing, or no Java runtime) — an
            environment problem, not the learner's work

Spec keys:
    entry: str            function name to call (default "transform")
    inputs: {name: rows}  ordered named DataFrames, passed positionally
    expect: [rows]        expected output rows (list of dicts)
    ordered: bool         compare row order too (default false)
    partitions: int       optional: assert result.rdd.getNumPartitions() == N
"""

from __future__ import annotations

import importlib.util

from ..context import Context
from ..registry import CheckType, register
from ..result import CheckResult


def _load_fn(path, name):
    spec = importlib.util.spec_from_file_location("spark_submission", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # may raise on bad learner code — caller catches
    return getattr(mod, name, None)


def _norm(value):
    """Coerce numbers so 100, 100.0 and Decimal('100') compare equal."""
    from decimal import Decimal

    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, Decimal)):
        return round(float(value), 6)
    return value


def _key(row: dict):
    return tuple(sorted((k, _norm(v)) for k, v in row.items()))


def _rows_equal(got: list[dict], expect: list[dict], ordered: bool) -> bool:
    if len(got) != len(expect):
        return False
    if ordered:
        return all(_key(g) == _key(e) for g, e in zip(got, expect))
    return sorted(map(_key, got)) == sorted(map(_key, expect))


@register("spark")
class SparkCheck(CheckType):
    def run(self, ctx: Context) -> CheckResult:
        try:
            from pyspark.sql import DataFrame, SparkSession
        except ImportError:
            return self._error(
                "PySpark isn't installed — run `pip install pyspark` "
                "(and make sure a Java runtime is available)."
            )

        try:
            spark = (
                SparkSession.builder.master("local[*]")
                .appName("grader-spark")
                .config("spark.ui.enabled", "false")
                .config("spark.sql.shuffle.partitions", "4")
                .getOrCreate()
            )
            spark.sparkContext.setLogLevel("ERROR")
        except Exception as exc:  # noqa: BLE001 - Java missing etc. = environment
            return self._error(
                f"couldn't start Spark ({exc}). Is a Java runtime installed?"
            )

        entry = self.spec.get("entry", "transform")
        inputs = self.spec.get("inputs") or {}
        expect = self.spec.get("expect") or []
        ordered = bool(self.spec.get("ordered", False))
        want_partitions = self.spec.get("partitions")

        # Build the input DataFrames in declared order.
        try:
            input_dfs = [spark.createDataFrame(rows) for rows in inputs.values()]
        except Exception as exc:  # noqa: BLE001 - malformed task inputs = author bug
            return self._error(f"could not build Spark inputs from the task spec: {exc}")

        # Load + run the learner's function (their errors are FAILs, not ERRORs).
        try:
            fn = _load_fn(ctx.submission_path, entry)
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"your code failed to import: {exc}")
        if fn is None:
            return self._fail(f"define a function named `{entry}(...)` in your submission")

        try:
            result = fn(*input_dfs)
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"your transform errored: {exc}")

        if not isinstance(result, DataFrame):
            return self._fail(f"`{entry}(...)` must return a Spark DataFrame")

        if want_partitions is not None:
            got_partitions = result.rdd.getNumPartitions()
            if got_partitions != want_partitions:
                return self._fail(
                    f"expected {want_partitions} partitions, got {got_partitions} — "
                    "use repartition(...) to control parallelism"
                )

        try:
            got = [row.asDict() for row in result.collect()]
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"couldn't collect your DataFrame's rows: {exc}")

        if not _rows_equal(got, expect, ordered):
            return self._fail(
                f"the rows don't match — expected {len(expect)} row(s) like "
                f"{expect[0] if expect else '{}'}, got {len(got)}"
            )
        return self._pass()
