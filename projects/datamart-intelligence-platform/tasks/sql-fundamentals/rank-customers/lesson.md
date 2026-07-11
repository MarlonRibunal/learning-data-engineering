# Window functions: RANK

**The scenario.** You want each customer's total spend **and** their rank — #1
spender, #2, and so on. A `GROUP BY` can give you the totals, but it throws the
rows away, so it can't easily number them. **Window functions** compute across a
set of rows *while keeping them* — the capstone skill of analytics SQL.

## RANK over an ordering

```sql
SELECT customer_id,
       SUM(total_amount) AS total_spend,
       RANK() OVER (ORDER BY SUM(total_amount) DESC) AS spend_rank
FROM orders
GROUP BY customer_id;
```

- **`GROUP BY customer_id`** first collapses to one row per customer with their
  `total_spend`.
- **`RANK() OVER (ORDER BY SUM(total_amount) DESC)`** then numbers those rows —
  biggest spender gets rank 1. The `OVER (...)` clause is what makes it a
  *window* function: it defines the set of rows and their order.
- You can rank *within groups* too by adding `PARTITION BY` inside `OVER` (e.g.
  rank customers within each region) — you'll use that constantly.

`RANK` leaves gaps after ties (1, 2, 2, 4); `DENSE_RANK` doesn't (1, 2, 2, 3);
`ROW_NUMBER` forces a unique number even on ties. Reach for the one that fits.

## Your task

Return each **`customer_id`**, its **`total_spend`**, and its **`spend_rank`**
(highest spender = 1).
