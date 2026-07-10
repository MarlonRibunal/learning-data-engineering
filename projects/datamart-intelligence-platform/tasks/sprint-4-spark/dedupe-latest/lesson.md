# Keep the latest record per key

**The scenario.** A raw feed has the same entity multiple times — an order that
was updated twice, a customer record replayed. You want **one row per key: the
newest one.** `dropDuplicates()` won't do — it keeps an *arbitrary* row, so your
results change run to run. The reliable pattern uses a **window** to rank each
key's rows by time and keep rank 1.

## The pattern (row_number + filter)

```python
from pyspark.sql import functions as F, Window

w = Window.partitionBy("id").orderBy(F.col("ts").desc())
(events.withColumn("rn", F.row_number().over(w))
       .filter(F.col("rn") == 1))
```

- **`partitionBy("id")`** — number rows *within* each key.
- **`orderBy(ts desc)`** — newest first, so the latest gets `rn = 1`.
- **`row_number()`** (not `rank()`) — guarantees a single winner even if two
  timestamps tie.
- **`filter(rn == 1)`** — keep only the newest per key.

This is *the* canonical "latest-per-key" deduplication in Spark, and the same
shape works for "first event per session", "most recent price", etc.

## Your task

Write `transform(events)` (`id`, `ts` string, `v`) that keeps the newest row per
`id` and returns **`id`, `v`**. Remember to cast `ts` with `F.to_timestamp` so
ordering is chronological, not alphabetical.
