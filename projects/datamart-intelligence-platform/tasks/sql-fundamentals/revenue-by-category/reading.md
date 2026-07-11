## Aggregation and the shape of analytics

`GROUP BY` is the moment SQL stops being about *records* and starts being about
*insight*. It collapses many rows into a summary — the essence of **OLAP**
(online analytical processing), as opposed to **OLTP** (the transactional writes
that created the rows in the first place).

How does the engine actually group? Two classic strategies:

- **Hash aggregation** — build a hash table keyed by `category`, and accumulate a
  running `SUM` in each bucket as rows stream by. Fast, needs memory for the
  distinct keys.
- **Sort aggregation** — sort the rows by `category` so each group is contiguous,
  then sum each run. Cheaper on memory, costs a sort.

The planner picks based on data size and available memory — you just write
`GROUP BY` and get the right one.

Conceptually, an aggregate is a function that takes *many values* and returns
*one*: `SUM`, `COUNT`, `AVG`, `MIN`, `MAX`. That "many-to-one" is why every
non-aggregated column in your `SELECT` must appear in `GROUP BY` — otherwise the
engine wouldn't know which of the many values to show. This single rule, once it
clicks, explains most `GROUP BY` errors you'll ever hit.

*Go deeper: "The Data Warehouse Toolkit" (Kimball) on why analytics is
aggregation-shaped.*
