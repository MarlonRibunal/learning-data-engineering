**Real-time processing: windowing over event time.** A stream never ends, so you can't `GROUP BY` the whole thing — you aggregate over **time windows**: "orders per 10 minutes", "revenue per hour". This is the core of real-time analytics.

You'll use Spark's **event-time windowing** API — `window(ts, "10 minutes")` — the *exact* same code you'd run inside a Spark Structured Streaming query. Here you run it on a fixed batch of timestamped events so the results are deterministic and you can focus on the windowing logic itself.

You'll practice:
- **Tumbling windows** — fixed, non-overlapping buckets.
- **Windowed aggregation** — sum/count per window.
- **Sliding windows** — overlapping buckets that update more often.

> **Watermarks & state (concept).** On a live stream, events arrive late and out of order. A **watermark** (`.withWatermark("ts", "10 minutes")`) tells Spark how long to wait for stragglers before finalizing a window and dropping its state — the mechanism that keeps unbounded streaming state bounded. It's a no-op on this batch data, but it's the idea that makes the same windowing code safe on a real stream.

> Needs **Java 17 or 21** + `pip install pyspark` (same as the Spark sprint).
