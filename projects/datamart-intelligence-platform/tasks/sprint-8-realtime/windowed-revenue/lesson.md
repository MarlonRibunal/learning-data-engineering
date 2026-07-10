# Windowed aggregation

Counting events per window is useful; summing a metric per window is the real workhorse — "revenue per 10 minutes", "errors per minute", "clicks per hour".

```python
from pyspark.sql import functions as F

events \
    .withColumn("ts", F.to_timestamp("ts")) \
    .groupBy(F.window("ts", "10 minutes")) \
    .agg(F.sum("amount").alias("revenue"))
```

Same windowing as before, but instead of `.count()` you use `.agg(...)` with any aggregate — `F.sum`, `F.avg`, `F.max`, `F.approx_count_distinct`, and so on. This is exactly how a streaming dashboard computes a live per-minute metric.

## Your task

Given `events` (`ts` string, `category`, `amount`), write `transform(events)` returning one row per 10-minute window with:

- **`window_start`** — the window's start as a **string**,
- **`revenue`** — the sum of `amount` in that window.
