### Join tables and rank the results

Real questions span more than one table. The revenue lives in `orders`, but the
customer's name lives in `customers`. A **JOIN** stitches them together on a shared
key (`customer_id`).

**Your task:** show the **top 3 customers by total spend** — their `customer_name`
and total spend, highest first.

```
SELECT c.customer_name, SUM(o.total_amount) AS total_spend
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_name
ORDER BY total_spend DESC
LIMIT 3;
```

This one move — join, aggregate, sort, limit — is the backbone of most analytics
queries you'll ever write.
