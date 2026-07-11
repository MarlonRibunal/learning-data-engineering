## ACID on object storage: the transaction log

`MERGE` on a lake feels ordinary until you remember object storage has **no
transactions**: files are immutable, writes aren't atomic across files, and
readers can see half-written state. Delta Lake, Iceberg, and Hudi solve this the
same way — a **transaction log**.

Instead of mutating data files, every change *appends a commit* to an ordered log
(Delta's `_delta_log`) recording which files were added and removed. That log is
the source of truth, and it delivers the ACID guarantees a warehouse has:

- **Atomicity** — a `MERGE` either fully commits or not at all; no half-applied
  upserts.
- **Isolation** — readers see a consistent snapshot (the log state at their start)
  even while a writer commits; optimistic concurrency resolves conflicts.
- **Consistency & durability** — schema is enforced on write; the log is durable.

`MERGE` is the operation this unlocks: applying CDC feeds, SCD updates, and
incremental loads *transactionally* on cheap storage — the ingestion patterns you
learned, now safe on a lake. The log also powers schema evolution, and (next
level) **time travel**, since every past commit is still recorded.

These **table formats** (Delta/Iceberg/Hudi) are the foundation of the modern
lakehouse — the layer that made "database on a data lake" real.

*Go deeper: Delta Lake transaction log; ACID on object storage; Iceberg/Hudi;
optimistic concurrency.*
