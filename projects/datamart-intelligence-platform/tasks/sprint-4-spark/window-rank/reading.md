## Window functions on a cluster

Window functions feel like SQL magic; on Spark they're a distributed operation
with real mechanics worth understanding.

A window with `partitionBy(key)` is, under the hood, a **shuffle** — Spark moves
all rows for a partition key onto the same executor (so it can rank/number them
together), then sorts within each. So `Window.partitionBy(...).orderBy(...)` costs
about what a `groupBy` + sort costs; it's a wide operation, not free syntax.

Two practical consequences:

- **Skew hits windows too.** If one partition key holds most of the rows, that
  executor becomes a straggler — the same skew problem as joins.
- **Unpartitioned windows are dangerous.** `Window.orderBy(...)` with *no*
  `partitionBy` forces *all* data onto a **single** partition (one machine) to
  establish a global order — fine on small data, a scalability cliff on big data.
  Always partition when you can.

Spark's **Catalyst** optimizer plans all this; **Tungsten** (its execution engine)
runs it with compiled, memory-efficient code. Windows are where "SQL you know"
meets "distributed cost you must respect."

*Go deeper: window exec & shuffles in Spark; skew; the perils of a global order.*
