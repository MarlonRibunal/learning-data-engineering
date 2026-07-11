# Running total of revenue

**The scenario.** Finance doesn't just want "revenue per day" — they want the
line that climbs toward the monthly goal: **revenue to date**. That's a running
(cumulative) total, and window functions compute it without collapsing your
rows.

## The pattern

`SUM(...) OVER (ORDER BY ...)` is a window function that sums **every row up to
and including the current one**, in the given order:

```sql
SELECT order_date,
       SUM(total_amount) OVER (ORDER BY order_date) AS cumulative_revenue
FROM orders
ORDER BY order_date;
```

- The `OVER (ORDER BY order_date)` turns `SUM` from a grouping aggregate into a
  **running** one — each row sees all earlier rows plus itself.
- No `GROUP BY`: every order stays as its own row, gaining a cumulative column.
- The final `ORDER BY` makes the output read top-to-bottom in date order (this
  task checks the row **order**, so keep it).

## Your task

Write `running_total_revenue.sql` returning `order_date` and a
`cumulative_revenue` running total, ordered by date. The last row's cumulative
value should equal the grand total of all orders.
