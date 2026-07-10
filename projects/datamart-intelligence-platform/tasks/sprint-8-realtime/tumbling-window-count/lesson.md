# Tumbling windows

A **tumbling window** chops the timeline into fixed, non-overlapping buckets — 09:00–09:10, 09:10–09:20, and so on. Every event lands in exactly one.

```python
from pyspark.sql import functions as F

events \
    .withColumn("ts", F.to_timestamp("ts")) \
    .groupBy(F.window("ts", "10 minutes")) \
    .count()
```

- **`F.to_timestamp("ts")`** — the incoming `ts` is a string; window functions need a real timestamp, so cast it first.
- **`F.window("ts", "10 minutes")`** — buckets rows by event time. It produces a `window` struct with `.start` and `.end`.
- **`.count()`** — one count per window.

Window boundaries align to the clock (…09:00, 09:10, 09:20…), so they're the same every run.

## Your task

Given `events` (`ts` string, `category`, `amount`), write `transform(events)` that returns one row per 10-minute window with:

- **`window_start`** — the window's start as a **string** (`F.col("window.start").cast("string")`),
- **`count`** — how many events fell in that window.
