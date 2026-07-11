## Window functions: aggregate without collapsing

Window functions are the feature that turns SQL from "reporting" into genuine
**analytics**. The insight: a `GROUP BY` aggregate *collapses* its rows into one;
a **window** aggregate computes across a set of related rows but **keeps every
row**. Same math, but you retain the detail *and* the summary side by side.

The `OVER (...)` clause defines that "window" of related rows:

- **`PARTITION BY`** — split rows into independent groups (rank customers *within
  each region*). Like `GROUP BY`, but the rows survive.
- **`ORDER BY`** (inside `OVER`) — order rows within the partition, which is what
  ranking and running totals need.
- **Frame** (`ROWS BETWEEN ...`) — for running/moving calculations, defines *how
  many* surrounding rows each computation sees (e.g. "the 3 rows before this
  one" for a moving average).

This unlocks a whole class of questions that are painful without it: rank within
group, running total, moving average, "this row vs. the previous row" (`LAG`/
`LEAD`), top-N-per-group, percentiles.

Ranking has three flavors worth knowing: `RANK` (gaps after ties: 1,2,2,4),
`DENSE_RANK` (no gaps: 1,2,2,3), and `ROW_NUMBER` (unique even on ties: 1,2,3,4).

Master windows and you can express almost any analytical question in one query —
which is why they're the hallmark of a strong SQL practitioner.

*Go deeper: "SQL Window Functions" tutorials; the `LAG`/`LEAD`/frame clauses.*
