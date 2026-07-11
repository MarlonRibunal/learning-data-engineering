## Change Data Capture

Copying a whole source table every night is wasteful and always slightly stale.
**Change Data Capture (CDC)** flips the model: instead of re-reading state, you
consume the *stream of changes* — every insert, update, and delete as it happens.

Where the change feed comes from:

- **Log-based CDC** (the gold standard) reads the database's own transaction log
  (Postgres WAL, MySQL binlog). Tools like **Debezium** turn that log into a
  stream. It's low-overhead and catches *every* change, including deletes.
- **Query-based CDC** polls `WHERE updated_at > last_seen`. Simpler, but misses
  hard deletes and depends on a reliable timestamp column.

Applying a change feed forces two design choices you met in this task:

- **Inserts and updates unify** into an **upsert** against the target's key.
- **Deletes** are usually **soft** in a warehouse (`is_deleted = true`), not
  physical — you preserve history so past reports stay reproducible.

CDC is the backbone of modern replication and real-time analytics (Fivetran,
Debezium, Kafka Connect all speak it) — moving *changes*, not *snapshots*.

*Go deeper: Debezium / log-based CDC; soft deletes and slowly changing data.*
