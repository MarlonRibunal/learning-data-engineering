## Precompute vs. compute-on-read

A running total is cheap on 5 rows and expensive on 5 billion. Serving is full of
this tension: should a metric be **computed when queried**, or **precomputed and
stored**?

- **Compute-on-read** (a window function in the dashboard's query) — always
  current, nothing to maintain, but every viewer pays the cost, every time.
- **Precompute** (materialize the running total in a nightly job) — instant reads
  for everyone, at the cost of storage and a rebuild that can go stale between
  runs.

Real BI stacks blend these with a hierarchy of aggregation:

- **Rollup / aggregate tables** — pre-summarized (revenue by day, by month) so
  dashboards read summaries, not raw events.
- **Materialized views / OLAP cubes** — the database maintains a precomputed
  result and refreshes it.
- **BI extracts** (Tableau/Power BI) — a cached snapshot pushed close to the user.

The engineering skill is picking the right point on that spectrum per metric:
freshness needs, data volume, and how many people read it. A running total on a
huge fact table is exactly the kind of thing you precompute.

*Go deeper: aggregate/rollup tables; materialized views; OLAP cubes.*
