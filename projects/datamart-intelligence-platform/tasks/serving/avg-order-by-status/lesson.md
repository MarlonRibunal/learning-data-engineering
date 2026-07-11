# Average order value by status

**The scenario.** "Do cancelled orders skew smaller? Are shipped orders our big
tickets?" A per-status **average** answers it — a classic slice-the-metric-by-a-
dimension serving query, and the shape behind half the tiles on any dashboard.

## Aggregate per group

`GROUP BY` the dimension, apply the aggregate, and round money to cents:

```sql
SELECT status,
       ROUND(AVG(total_amount), 2) AS avg_order_value
FROM orders
GROUP BY status;
```

- **`AVG`** (not `SUM`) — the *average* order value, not the total. Mixing these
  up is the most common slip here.
- **`ROUND(..., 2)`** keeps currency to two decimals so the tile reads cleanly.
- One row per `status`.

## Your task

Write `avg_order_by_status.sql` returning each `status` and its
`avg_order_value` — the rounded average `total_amount` for orders in that status.
