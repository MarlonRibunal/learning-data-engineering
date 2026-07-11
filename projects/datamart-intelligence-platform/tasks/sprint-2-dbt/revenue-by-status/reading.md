## Materialization and the layers of a warehouse

When dbt turns your `SELECT` into a table, *how* it stores it is the
**materialization**, and you choose it:

- **view** — dbt stores just the query; it runs fresh every time it's read.
  Always current, zero storage, but recomputes on each query. Good for light,
  frequently-changing logic.
- **table** — dbt runs the query and stores the *result*. Fast to read, but
  rebuilt on each `dbt run`. Good for heavy models read many times (like this
  revenue mart).
- **incremental** — dbt only processes *new* rows each run and appends them.
  Essential once a table is too big to rebuild from scratch nightly.

Materializations are why dbt models are organized in **layers**:

- **staging** — light views that clean and rename raw columns (one per source).
- **marts** — the business-facing tables (like `revenue_by_status`) that
  aggregate staging models into what analysts actually query.

This layering (raw → staging → marts) is the standard dbt project shape. It keeps
transformations modular: fix a rename once in staging, and every mart downstream
inherits it.

*Go deeper: dbt "Materializations"; the staging/marts project structure.*
