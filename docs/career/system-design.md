# Data Engineering System Design

"Design a pipeline that…" is the round that most separates junior from senior.
There's no single right answer — they're testing how you **reason**. Use a
consistent frame.

## A frame that always works

1. **Clarify** — volume, velocity, latency SLA (batch? near-real-time?),
   consumers (BI? ML? ops?), correctness needs (exactly-once?).
2. **Sketch the lifecycle** — Generation → Ingestion → Storage → Transformation
   → Serving, plus the undercurrents (quality, security, cost). This repo is
   organized exactly this way — walk it.
3. **Pick components with reasons** — name a tool *and* why (e.g. "Airflow for
   batch orchestration because dependencies are a DAG and retries matter").
4. **Address the hard parts explicitly** — late data, schema evolution,
   idempotency/backfills, failure & recovery, monitoring.
5. **State trade-offs** — every choice costs something; naming the cost is the
   senior signal.

## The undercurrents interviewers probe

- **Quality:** where do you validate, and what happens on failure?
- **Idempotency & backfills:** can you safely rerun any step?
- **Freshness & monitoring:** how do you know it's healthy — before a user does?
- **Security:** least privilege, PII handling (you did both in *Security*).
- **Cost:** partitioning, incremental vs. full loads, storage tiers.

## Worked micro-example: "real-time revenue dashboard"

Ingest orders to a stream (Redpanda) → windowed aggregation with a watermark
for late orders (Spark structured streaming) → serve a rollup table → a
dashboard reads KPI/series functions. Trade-off: windowing + watermark adds
latency (you wait for stragglers) in exchange for correctness. You've built
**every stage of this** in the streaming, real-time, serving, and dashboard
sprints — use it as your go-to example.
