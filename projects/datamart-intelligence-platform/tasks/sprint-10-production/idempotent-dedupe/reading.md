## Idempotency, replay, and reprocessing

You met idempotency in ingestion; production is where it earns its keep at scale.
The reason it's *the* production pattern is that real pipelines **reprocess** all
the time, and every reprocess is a bet that running twice equals running once.

When reprocessing happens (whether you plan it or not):

- **Retries** re-run a failed task — possibly after it partially wrote.
- **Backfills** deliberately re-run historical partitions to fix a bug or add a
  column.
- **Replays** re-read a stream from an old offset after a downstream error.
- **Duplicate delivery** — at-least-once messaging redelivers the same event.

Idempotent processing (dedupe by key, upsert, "replace this partition" instead of
"append") makes all four *safe*. Without it, each is a data-corruption event.

The production framing worth internalizing: **design every write to be re-runnable
from the start**, because you can't predict when a retry or backfill will hit it,
and retrofitting idempotency after a double-count incident is painful. "Can I
safely run this again?" should be a yes for every task you ship.

*Go deeper: idempotent writes; backfill/replay safety; reprocessing strategies.*
