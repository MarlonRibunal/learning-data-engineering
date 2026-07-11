## Delivery semantics: the three guarantees

Deduplicating by offset exists because of the central bargain of distributed
messaging: you get to pick **one** of three delivery guarantees, and each has a
cost.

- **At-most-once** — commit the offset *before* processing. If you crash mid-
  process, that message is lost. Fast, no duplicates, but data loss on failure.
  Acceptable only for metrics you can afford to drop.
- **At-least-once** — commit *after* processing. A crash before committing means
  you reprocess on restart → **duplicates**. No data loss, but you *will* see the
  same message twice. This is the pragmatic default.
- **Exactly-once** — every message affects the result once, even across failures.
  The ideal, but expensive: it needs transactions or idempotency end to end.

The practical path to "effectively exactly-once" is **at-least-once delivery + an
idempotent consumer**: accept that you'll see duplicates, and make processing
immune to them — dedupe by the message's unique offset/id (this task), or upsert by
a key (the ingestion sprint). The offset is a perfect dedup key because it's
unique and monotonic per partition.

This is the streaming face of the idempotency you drilled in ingestion: the
network *will* redeliver, so correctness means designing for it.

*Go deeper: at-most/at-least/exactly-once; idempotent consumers; the offset as a
dedup key.*
