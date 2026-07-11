## Landing zones and messy sources

Ingestion's first law: **raw data is dirty, and that's not your source's fault —
it's reality.** Systems retry, webhooks double-fire, exports overlap. So you never
load a source feed straight into your clean tables. You land it *as-is* in a
**landing zone** (here, `landing.products_raw`), then clean it into `raw`.

That two-hop shape — **land raw, then transform** — is deliberate:

- The landing copy is an **immutable record** of exactly what arrived; if your
  cleaning logic has a bug, you can reprocess from landing without re-fetching.
- Cleaning (dedup, type-cast, validate) happens *in* the warehouse, where it's
  cheap, versioned, and testable — the ELT philosophy again.

Deduplicating "keep the latest per key" is the most common first cleaning step,
because most sources deliver **at-least-once**: you *will* see the same record
more than once, and your job is to make the target reflect it exactly once.

*Go deeper: "landing zone / raw layer" patterns; at-least-once delivery.*
