# Rank categories by revenue

**The scenario.** The "Top Categories" panel on a dashboard needs each category's
revenue **and its rank** — #1 seller, #2, and so on. `RANK()` is the window
function that numbers rows by a metric.

## Combining an aggregate with a window

You can rank the *result* of a `GROUP BY` — aggregate first, then rank the
totals:

```sql
SELECT category,
       SUM(total_amount) AS revenue,
       RANK() OVER (ORDER BY SUM(total_amount) DESC) AS rank
FROM orders
GROUP BY category;
```

- `GROUP BY category` collapses to one row per category with its `revenue`.
- `RANK() OVER (ORDER BY SUM(total_amount) DESC)` numbers those category rows,
  biggest revenue = rank 1.
- You can use the aggregate `SUM(total_amount)` directly inside the window's
  `ORDER BY` — no subquery needed.

## Your task

Write `rank_categories.sql` returning `category`, its `revenue`
(sum of `total_amount`), and its `rank` (highest revenue = 1).
