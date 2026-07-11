# Aggregate with GROUP BY

**The scenario.** "Which product categories make us the most money?" You can't
answer that row by row — you have to **roll many rows up** into one per category,
summing the revenue. That's aggregation, the heart of analytics.

## GROUP BY + an aggregate

```sql
SELECT category, SUM(total_amount) AS revenue
FROM orders
GROUP BY category
ORDER BY revenue DESC;
```

Read it as a pipeline:

1. **`GROUP BY category`** — bucket the rows, one bucket per distinct category.
2. **`SUM(total_amount)`** — collapse each bucket to a single summed value.
3. **`AS revenue`** — name that computed column so it's readable.
4. **`ORDER BY revenue DESC`** — sort biggest first, so the top earner is on top.

**The rule to remember:** every column in your `SELECT` must either be **in the
`GROUP BY`** or wrapped in an **aggregate** (`SUM`, `COUNT`, `AVG`, `MIN`,
`MAX`). Mixing a plain column with an aggregate without grouping it is the most
common `GROUP BY` error.

## Your task

Return one row per **`category`** with its total **`revenue`** (sum of
`total_amount`), sorted highest revenue first. Hit **▶ Run query** to see your
rows, then **Check my work**.
