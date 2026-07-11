### Compare against an aggregate with a subquery

A **subquery** is a query nested inside another, wrapped in parentheses. A common use
is comparing each row against an aggregate of the whole table — like "rows above the
average."

**Your task:** return the orders whose `total_amount` is greater than the average
`total_amount` across all orders.

```
SELECT *
FROM orders
WHERE total_amount > (SELECT AVG(total_amount) FROM orders);
```

The inner query runs first and produces a single value; the outer query compares each
row against it.
