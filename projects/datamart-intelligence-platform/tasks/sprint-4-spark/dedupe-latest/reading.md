## Why "just dropDuplicates" isn't enough

Deduplication looks trivial and is quietly full of traps at scale — which is why
you used a window (`row_number`) instead of `dropDuplicates()`.

- **`dropDuplicates()` is non-deterministic** on partial keys. Ask it to dedupe by
  `id` and it keeps an **arbitrary** row per id — whichever the shuffle happened to
  surface. Run the job twice, get different survivors. For "keep the *latest*," you
  must rank by a timestamp and take rank 1, which is deterministic.

- **Dedup is a shuffle.** Both `dropDuplicates` and the window group rows by key
  across the cluster — a wide, expensive operation, and a magnet for **skew** if
  one key is heavily duplicated.

- **Distributed dedup can't "just use a set."** On one machine you'd throw values
  in a hash set. Across a cluster there's no shared set, so Spark shuffles like
  keys together first — which is exactly what makes it costly.

The deeper theme: at scale, correctness needs an explicit *tiebreak* (latest-wins),
and every "remove duplicates" is really a "move all copies of each key to one
place" — a shuffle you should see coming.

*Go deeper: `dropDuplicates` semantics; `row_number` latest-per-key; dedup skew.*
