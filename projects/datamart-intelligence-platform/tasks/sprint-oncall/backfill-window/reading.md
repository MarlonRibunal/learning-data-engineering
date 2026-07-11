## Backfills: correctness at the boundaries

After a fix, you must **backfill** the window the pipeline missed — and backfills
are where careful engineers earn their reputation, because the bugs all live at the
boundaries.

- **No gaps, no overlaps.** Reprocess one day too few → a permanent hole in your
  data. Re-run the last good day → risk double-counting. The correct window is
  "the day *after* the last success through today" — exactly the boundary logic you
  implemented.
- **Backfills demand idempotency.** A backfill *re-runs intervals*, so unless each
  interval's write is idempotent (replace-partition, upsert), the backfill itself
  corrupts data. This is why Airflow keys runs to data intervals and why you drilled
  idempotency so hard — backfill is *the* moment it pays off.
- **Order and scale.** Backfilling a year means many runs; run them in dependency
  order, and beware overwhelming shared resources (throttle concurrency — the
  thundering-herd lesson again).
- **Bounded scope.** Backfill *only* the affected window. "Just re-run everything"
  is expensive and risks touching data that was fine.

A clean backfill is idempotent writes over a precisely-bounded interval — the
difference between quietly repairing history and quietly corrupting it.

*Go deeper: backfill strategies; interval boundaries; idempotent reprocessing.*
