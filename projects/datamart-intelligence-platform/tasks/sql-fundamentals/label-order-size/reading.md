## Transform at read time vs. write time

`CASE` produces a **derived column** — a value computed from other columns rather
than stored. That raises a design question you'll face constantly as a data
engineer: should a value be *computed when you read* or *stored when you write*?

- **Compute at read (like `CASE` in a query):** always consistent with the source
  data, costs a little CPU each query, and changes instantly when you edit the
  logic. Great for labels, buckets, and anything whose definition might evolve.
- **Store at write (materialize the label in a column/table):** faster to read
  repeatedly, but now it can drift from the source and every definition change
  needs a backfill.

Most transformation layers (dbt models, this course's warehouse marts) are
exactly this tension made concrete: they *materialize* computed columns so
dashboards read them cheaply, accepting the cost of rebuilding when logic
changes.

`CASE` itself is SQL's general conditional. Beyond labeling, its most powerful
use is **conditional aggregation** — `SUM(CASE WHEN status = 'shipped' THEN
total_amount ELSE 0 END)` computes "shipped revenue" and "total revenue" in one
pass, pivoting rows into columns. That pattern shows up everywhere once you see
it.

*Go deeper: read about "pivoting with CASE" and the read-time vs. write-time
trade-off in analytics engineering.*
