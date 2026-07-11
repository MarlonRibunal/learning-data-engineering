## Snapshots and reconstructing the past

An SCD tracks history for *slowly*-changing attributes. But some questions need
the state of a *fast*-changing metric at a point in time: "how many orders were
`pending` **each day last month**?" A raw table only knows *now*, so you can't
answer it after the fact — unless you **snapshotted**.

A **snapshot table** appends a full (or filtered) copy of current state every
period, stamped with a `snapshot_date`. Over time it becomes a flip-book: query
`WHERE snapshot_date = '...'` to see the world as it was on any day.

Kimball formalizes two flavors:

- **Periodic snapshot** (this task) — a regular photo of state (daily inventory,
  daily open orders). Great for trends and point-in-time reporting.
- **Accumulating snapshot** — one row per process instance, updated as it moves
  through milestones (order placed → shipped → delivered), measuring durations
  between stages.

Modern warehouses also offer **time travel** (Snowflake, Delta, Iceberg) — query
a table "as of" a past timestamp without building snapshots yourself. But explicit
snapshots remain the portable, auditable way to freeze history you'll need later —
because the one thing you can't do is snapshot the past *retroactively*.

*Go deeper: periodic vs. accumulating snapshots; warehouse time travel
(Snowflake/Delta/Iceberg).*
