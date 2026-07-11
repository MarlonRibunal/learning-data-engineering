## What happens when you filter

`WHERE` is **selection** in relational algebra — keeping the rows that satisfy a
predicate. Conceptually the database tests every row; in practice it works hard
to avoid that.

- **Indexes.** An index is a sorted, searchable structure (usually a B-tree) on a
  column. With one on `status`, the engine can jump straight to the `'shipped'`
  rows instead of scanning the whole table — the difference between O(log n) and
  O(n). This is why the columns you filter on most are the ones you index.
- **Predicate pushdown.** In a data pipeline, the same `WHERE` can be *pushed
  down* to the storage layer so the filter happens as data is read, not after —
  less data moved, less work done. Warehouses and Spark do this automatically
  when they can.
- **Three-valued logic.** SQL predicates are true, false, **or unknown**. Compare
  anything to `NULL` and you get *unknown*, which `WHERE` treats as "don't
  include." That's why `WHERE x = NULL` returns nothing and you must write
  `WHERE x IS NULL`. This trips up nearly everyone once.

So filtering is where SQL's "describe what you want" philosophy pays off: you
state the predicate, and decades of engineering — indexes, pushdown, planners —
decide how to satisfy it fast.

*Go deeper: "Database Internals" (Alex Petrov) on B-trees; the SQL `NULL`
semantics in any reference.*
