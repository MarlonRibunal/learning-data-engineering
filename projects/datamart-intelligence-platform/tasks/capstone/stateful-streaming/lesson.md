# Capstone: the Stateful Streaming Monitor

The batch capstones proved you can build a warehouse and run an incident. This
one proves you can build the hardest thing in the course: a **real, stateful
streaming pipeline**. You'll write **one file** with three Spark Structured
Streaming queries — each a watermarked, stateful windowed aggregation — and the
grader runs them as *actual streaming jobs* (`readStream → writeStream`), not
batch. Pass all three and you earn a portfolio artifact.

## Why "stateful"?

A streaming aggregation can't see all its data at once — it arrives over time. So
the engine **holds state** for each open window and updates it as events stream
in, using a **watermark** to know when a window is complete and its state can be
dropped. That's what makes these queries *stateful* (and what keeps their memory
bounded on an infinite stream).

## The pipeline

```
event stream ──readStream──▶ watermark + window ──▶ revenue / active-users per window ──max──▶ 🔔 peak window
```

Each function takes the streaming `events` DataFrame and returns a transformed
**streaming** DataFrame — cast `ts`, add `.withWatermark("ts", "10 minutes")`,
window, aggregate, project `window.start` to a string. Don't call actions
(`.collect()`); return the stream and let the grader run it.

### Stage 1 — `windowed_revenue(events)`
`sum(amount)` per 10-minute window → `window_start`, `revenue`.

### Stage 2 — `active_users(events)`
Distinct users per 10-minute window → `window_start`, `active_users`. Use
`F.approx_count_distinct("user")` — the streaming-idiomatic distinct that keeps
state bounded (a HyperLogLog sketch) instead of remembering every user forever.

### Stage 3 — `peak_window(events)`
The single window with the highest revenue → `window_start`, `revenue`
(`.orderBy(F.col("revenue").desc()).limit(1)`).

## Your task

Fill in all three streaming functions in `streaming_pipeline.py`. Together they
are a live monitor over an order stream — the streaming half of the craft, done
for real.
