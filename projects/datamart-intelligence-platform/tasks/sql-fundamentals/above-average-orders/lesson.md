# Subqueries

**The scenario.** "Show me the orders bigger than average." The catch: you don't
*know* the average until you've scanned the whole table — and you need that one
number to filter individual rows. A **subquery** lets you compute it inline and
use it right where you need it.

## A query inside a query

```sql
SELECT *
FROM orders
WHERE total_amount > (SELECT AVG(total_amount) FROM orders);
```

- The inner query **`(SELECT AVG(total_amount) FROM orders)`** runs first and
  returns a single value — the overall average.
- The outer `WHERE` then compares each row's `total_amount` against that value.

This kind of inner query — one that returns a single value — is a **scalar
subquery**, and it can sit anywhere a value can: in `WHERE`, in `SELECT`, in
`HAVING`. Subqueries let you build an answer in layers: compute a summary, then
use it to filter or enrich the detail.

## Your task

Return **every column** of the orders whose `total_amount` is **above the average**
`total_amount` across all orders.

```sql
SELECT *
FROM orders
WHERE total_amount > (SELECT AVG(total_amount) FROM orders);
```
