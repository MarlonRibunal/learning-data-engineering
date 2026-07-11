# Capstone: the Real-Time Revenue Monitor

This is a capstone — you're not learning one new trick, you're **assembling** the
real-time skills you've built into a single pipeline a company would actually
run: a monitor that watches a stream of order events and fires when a time window
spikes.

You'll write **one PySpark file** with three functions — the three stages of the
pipeline. Each is graded on a real Spark session, and passing all three emits a
**portfolio artifact** you can commit to your own GitHub.

## The pipeline

```
raw events ──clean──▶ valid events ──window + sum──▶ per-window revenue ──max──▶ 🔔 busiest window
```

### Stage 1 — `clean(events)`
Streams carry junk — here, events with a non-positive `amount` (a bug or a
correction). Drop them; keep `ts`, `category`, `amount`.

```python
def clean(events):
    return events.filter(F.col("amount") > 0).select("ts", "category", "amount")
```

### Stage 2 — `windowed_revenue(events)`
Aggregate the (clean) events into 10-minute event-time windows, summing revenue —
the live per-window metric. Return `window_start` (string) and `revenue`.

### Stage 3 — `busiest_window(events)`
The alert: find the **single** window with the highest revenue — the peak the
monitor pages on. Return that one `window_start` and its `revenue`.
(`.orderBy(F.col("revenue").desc()).limit(1)`.)

## Your task

Fill in all three functions in `realtime_pipeline.py`. Cast `ts` with
`F.to_timestamp` where you window, and project `window.start` to a string —
exactly the moves from the Real-time sprint. Pass all three stages and your
portfolio artifact is generated.
