## An error taxonomy

Deciding what to retry forces the most useful classification in operations:
**transient vs. permanent** errors. Retrying blindly is a bug in both directions —
retry a permanent error and you fail slower; give up on a transient one and you
fail unnecessarily.

- **Transient (retryable).** Temporary conditions that a retry might clear: rate
  limits (`429`), server/gateway errors (`500/502/503/504`), timeouts, a brief
  network partition, a locked row. The request was fine; the *moment* wasn't.
- **Permanent (non-retryable).** The request itself is wrong and will fail every
  time: bad input (`400`), unauthorized (`401/403`), not found (`404`), a schema
  mismatch. Retrying just wastes time and hides the real problem; these need a fix,
  a dead-letter, or an alert.

The mapping isn't always the HTTP status — a `500` from a genuinely broken query is
"permanent" in disguise — but the status is the pragmatic first cut, which is why
production code keeps a **retryable set**.

This taxonomy underlies every resilient system: retry the transient (with backoff
and jitter), fail-fast the permanent (loudly), and dead-letter the un-processable.
Classifying the error correctly is the decision that everything downstream —
retries, alerts, circuit breakers — depends on.

*Go deeper: transient vs. permanent faults; retryable error sets; the dead-letter
path for permanent failures.*
