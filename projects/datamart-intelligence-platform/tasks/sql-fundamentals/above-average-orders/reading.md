## Composing queries

A subquery is the first step toward **query composition** — building a complex
answer from simpler pieces. Learning the kinds pays off:

- **Scalar subquery** — returns a single value, usable anywhere a value goes:
  `WHERE total_amount > (SELECT AVG(total_amount) FROM orders)`. The inner query
  runs once, produces one number, and the outer query uses it.
- **Correlated subquery** — references the outer row, so it re-evaluates per row:
  `WHERE total_amount > (SELECT AVG(total_amount) FROM orders o2 WHERE o2.category
  = orders.category)` ("above average *for its category*"). Powerful, but can be
  slow — it's a loop.
- **Subquery in `FROM`** (a derived table) — treat a query's result as a table to
  query further.

Modern SQL gives you a cleaner tool for composition: the **CTE** (Common Table
Expression), written with `WITH`:

```sql
WITH avg_order AS (SELECT AVG(total_amount) AS a FROM orders)
SELECT * FROM orders, avg_order WHERE total_amount > avg_order.a;
```

CTEs let you name each step and read a query top-to-bottom like a short program —
which is why dbt models and analytics SQL lean on them heavily. A subquery is
where that habit of *building answers in layers* begins.

*Go deeper: read about CTEs (`WITH`) and correlated vs. uncorrelated subqueries.*
