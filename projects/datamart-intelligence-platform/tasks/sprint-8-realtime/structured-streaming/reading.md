## The unbounded-table model and exactly-once

Spark Structured Streaming's core idea is disarmingly simple: **treat the stream
as an unbounded table** that new rows are continually appended to. Your query is a
standing query over that ever-growing table, and the engine keeps its result up to
date. That's why your batch DataFrame code runs unchanged on a stream.

Under the hood, Spark runs it as a series of tiny **micro-batches** (Flink, by
contrast, processes event-by-event — "continuous" — for lower latency). Two pieces
make it production-grade:

- **Checkpointing.** The engine persists its progress — which input offsets it has
  consumed and its aggregation state — to a checkpoint directory. On a crash it
  resumes from the last checkpoint instead of reprocessing from zero.
- **Exactly-once semantics.** Combine checkpointed offsets with **idempotent or
  transactional sinks**, and Spark guarantees each input contributes to the result
  *exactly once*, even across failures and retries — the hardest guarantee in
  streaming, and the reason all that idempotency work earlier mattered.

`trigger(availableNow)` (which the grader used) is a bridge between the worlds:
process all currently-available data as a bounded run, then stop — batch execution
on streaming infrastructure.

*Go deeper: micro-batch vs. continuous; checkpointing; exactly-once & the
output-mode/sink contract.*
