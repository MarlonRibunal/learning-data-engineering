"""Structured-streaming check: grade a learner's real Spark streaming transform.

The learner writes a function that takes a **streaming** DataFrame and returns a
transformed streaming DataFrame (typically a watermarked windowed aggregation).
The grader:

  1. writes the known events as JSON files to a temp source directory,
  2. opens them as a streaming DataFrame (readStream),
  3. calls the learner's transform,
  4. runs it to completion with a memory sink and trigger(availableNow) —
     bounded and deterministic — then compares the result to ``expect``.

    entry: str      function name, called as entry(events) (default stream_transform)
    inputs: {name: rows}   one named event stream (first entry is used)
    expect: [rows]  expected output rows
    ordered: bool   compare row order too (default false)

    PASS  - the streamed result matches
    FAIL  - learner code errored, returned a non-streaming DataFrame, or wrong rows
    ERROR - Spark can't run here (no pyspark / no Java)
"""

from __future__ import annotations

import importlib.util
import json
import os
import tempfile

from ..context import Context
from ..registry import CheckType, register
from ..result import CheckResult
from .spark_check import _rows_equal

_COUNTER = 0


def _load_fn(path, name):
    spec = importlib.util.spec_from_file_location("spark_stream_submission", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, name, None)


def _schema_for(row: dict):
    """Build a Spark schema from a sample row's Python types."""
    from pyspark.sql.types import (
        BooleanType, DoubleType, LongType, StringType, StructField, StructType,
    )

    def spark_type(v):
        if isinstance(v, bool):
            return BooleanType()
        if isinstance(v, int):
            return LongType()
        if isinstance(v, float):
            return DoubleType()
        return StringType()

    return StructType([StructField(k, spark_type(v)) for k, v in row.items()])


@register("spark_streaming")
class SparkStreamingCheck(CheckType):
    def run(self, ctx: Context) -> CheckResult:
        global _COUNTER
        try:
            from pyspark.sql import DataFrame, SparkSession
        except ImportError:
            return self._error("PySpark isn't installed — run `pip install pyspark`.")

        try:
            spark = (
                SparkSession.builder.master("local[*]")
                .appName("grader-spark-streaming")
                .config("spark.ui.enabled", "false")
                .config("spark.sql.shuffle.partitions", "2")
                .config("spark.sql.session.timeZone", "UTC")
                .getOrCreate()
            )
            spark.sparkContext.setLogLevel("ERROR")
        except Exception as exc:  # noqa: BLE001
            return self._error(f"couldn't start Spark ({exc}). Is a Java runtime installed?")

        entry = self.spec.get("entry", "stream_transform")
        inputs = self.spec.get("inputs") or {}
        expect = self.spec.get("expect") or []
        ordered = bool(self.spec.get("ordered", False))
        rows = next(iter(inputs.values()), [])
        if not rows:
            return self._error("task spec has no `inputs` events to stream")

        try:
            fn = _load_fn(ctx.submission_path, entry)
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"your code failed to import: {exc}")
        if fn is None:
            return self._fail(f"define a function named `{entry}(events)` in your submission")

        _COUNTER += 1
        qname = f"grader_out_{os.getpid()}_{_COUNTER}"
        src = tempfile.mkdtemp(prefix="grader-src-")
        ckpt = tempfile.mkdtemp(prefix="grader-ckpt-")
        query = None
        try:
            with open(os.path.join(src, "events.json"), "w") as fh:
                for r in rows:
                    fh.write(json.dumps(r) + "\n")

            events = spark.readStream.schema(_schema_for(rows[0])).json(src)
            result = fn(events)
            if not isinstance(result, DataFrame) or not result.isStreaming:
                return self._fail(
                    f"`{entry}(events)` must return a STREAMING DataFrame "
                    "(built from the streaming `events` — don't call an action on it)"
                )

            query = (
                result.writeStream.format("memory").queryName(qname)
                .outputMode("complete").option("checkpointLocation", ckpt)
                .trigger(availableNow=True).start()
            )
            query.awaitTermination(timeout=60)
            got = [row.asDict() for row in spark.sql(f"SELECT * FROM {qname}").collect()]
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"your streaming transform errored: {exc}")
        finally:
            if query is not None:
                try:
                    query.stop()
                except Exception:  # noqa: BLE001
                    pass

        if not _rows_equal(got, expect, ordered):
            return self._fail(
                f"the streamed result doesn't match — expected {len(expect)} row(s) "
                f"like {expect[0] if expect else '{}'}, got {len(got)}"
            )
        return self._pass()
