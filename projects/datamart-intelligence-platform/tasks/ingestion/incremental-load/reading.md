## Incremental loading and watermarks

Reloading an entire source every night works — until the source is a billion rows
and "every night" no longer fits in the night. **Incremental loading** processes
only what's *new* since last time, and it's how real pipelines stay affordable.

The classic mechanism is a **high-water mark**: remember the maximum
`loaded_at` (or an ever-increasing id) you've already ingested, and next run pull
only rows *beyond* it. The watermark is your bookmark into the source.

The subtleties that make it hard:

- **Late / out-of-order data** — a row with an old timestamp arriving after your
  watermark moved past it gets missed. (Streaming's watermark-with-allowed-
  lateness is the same problem, formalized.)
- **Idempotency at the boundary** — re-running the last increment must not
  double-load rows at the watermark edge, so incremental loads pair naturally with
  upserts.
- **Full-refresh escape hatch** — you still need the ability to reload everything
  when logic changes or a bug corrupts the target.

Incremental + idempotent is the combination that lets a pipeline run cheaply
*and* survive retries.

*Go deeper: high-water-mark / CDC-based incremental patterns; late-arriving data.*
