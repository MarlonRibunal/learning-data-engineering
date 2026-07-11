## Idempotency is the whole game

An **idempotent** operation produces the same result whether you run it once or a
hundred times. In data engineering this isn't a nicety — it's survival. Pipelines
retry on failure, backfills re-run history, streams redeliver messages. If loading
"today's data" a second time *doubles* it, your warehouse silently drifts from
truth.

An **upsert** (update-or-insert) is the canonical idempotent load. Postgres spells
it `INSERT ... ON CONFLICT (key) DO UPDATE`; the SQL standard calls it `MERGE`;
Spark/Delta has `MERGE INTO`. All express the same rule: *for each key, converge
the target to the source's value* — no duplicates on re-run.

Contrast the naive `INSERT`: run it twice, get two rows. That's **not**
idempotent, and it's the single most common data bug in existence.

The mental test to apply to every load you write: *"if this runs twice, is the
result identical to running once?"* If not, you have a latent double-counting bug
waiting for the next retry.

*Go deeper: idempotency, `MERGE`/upsert semantics, exactly-once vs at-least-once.*
