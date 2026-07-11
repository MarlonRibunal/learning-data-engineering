## Managed state: the hard part of streaming

This capstone is "stateful" because each query keeps **running state** that lives
*between* the micro-batches of an unbounded stream — and managing that state is
the genuinely hard engineering of stream processing.

What the engine is doing under your three queries:

- **A state store per key.** For every open window it holds a partial aggregate
  (a running sum, a HyperLogLog sketch for distinct users). As events stream in,
  it updates that state rather than recomputing from scratch.
- **Watermarks bound the state.** Without a bound, per-window state would grow
  forever. The watermark tells the engine when a window is final, so it emits the
  result and **evicts** the state — the only thing keeping memory finite on an
  infinite stream. Your `active_users` stage leans on this twice: watermark to
  bound *time*, and `approx_count_distinct` (a sketch) to bound *space*.
- **Checkpointing makes state durable.** The state store and input offsets are
  checkpointed, so a crashed job resumes with its state intact — the basis of
  exactly-once processing.

Beyond windowed aggregations, Spark exposes **arbitrary** stateful processing
(`flatMapGroupsWithState` / `applyInPandasWithState`) for custom logic —
sessionization, pattern detection, state machines over a stream — the frontier
where streaming gets genuinely powerful and genuinely tricky.

The two capstones you've now built — batch (accurate history) and streaming
(live present) — are the two halves of the craft. Managed, watermarked,
checkpointed state is what makes the streaming half work.

*Go deeper: streaming state stores; watermark-based eviction; checkpointing &
exactly-once; `flatMapGroupsWithState`.*
