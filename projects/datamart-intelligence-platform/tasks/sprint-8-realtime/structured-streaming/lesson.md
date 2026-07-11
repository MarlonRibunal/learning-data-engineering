# A real Structured Streaming query

**The scenario.** Everything so far windowed a *batch* of events — the logic is
identical to streaming, which is the whole point. Now you'll write it as an
actual **Spark Structured Streaming** query: the same code, but running against a
DataFrame that never ends.

The grader wires up the hard parts — it opens a **streaming** source, runs your
query with a memory sink and `trigger(availableNow)` (process everything, then
stop, so the result is deterministic), and reads back the output. **You write the
transform.**

## The transform

You're handed `events`, a *streaming* DataFrame (`events.isStreaming` is `True`).
Apply exactly what you'd apply on a stream:

```python
from pyspark.sql import functions as F

def stream_transform(events):
    return (events
        .withColumn("ts", F.to_timestamp("ts"))
        .withWatermark("ts", "10 minutes")           # bound state; drop late data
        .groupBy(F.window("ts", "10 minutes"))
        .count()
        .select(F.col("window.start").cast("string").alias("window_start"), "count"))
```

Two streaming-specific notes:

- **`withWatermark("ts", "10 minutes")`** tells Spark how long to wait for late
  events before it finalizes a window and forgets its state. On an unbounded
  stream this is what keeps memory from growing forever — the single most
  important line in a streaming aggregation.
- You **don't** call `.collect()` or `.show()` — a streaming DataFrame has no end
  to collect. You return the transformed *stream*; the grader starts and runs it.

## Your task

Write `stream_transform(events)` returning a streaming DataFrame of
**`window_start`** (string) and **`count`** per 10-minute event-time window, with
a watermark. Same numbers as the batch version — now truly streamed.
