### Rank rows with a window function

**Window functions** compute across a set of rows *related to the current row* without
collapsing them. `RANK() OVER (ORDER BY ...)` assigns a ranking — the analyst's
Swiss-army knife for "top N", running totals, and comparisons.

**Your task:** show `customer_id`, their total spend, and a `spend_rank` where 1 is the
highest spender.

```
SELECT customer_id,
       SUM(total_amount) AS total_spend,
       RANK() OVER (ORDER BY SUM(total_amount) DESC) AS spend_rank
FROM orders
GROUP BY customer_id;
```

`OVER (...)` is what makes it a window function. This is the most advanced core SQL
skill — get comfortable here and you can express almost any analytics question.
