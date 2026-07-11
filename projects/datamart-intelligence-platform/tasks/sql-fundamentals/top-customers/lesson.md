# Join two tables

**The scenario.** Orders know a `customer_id`, but not the customer's *name* —
that lives in the `customers` table. To report "top customers by spend" you have
to **join** the two tables on their shared key, then aggregate. Joining is how
you answer questions that span more than one table — most real questions.

## The pattern

```sql
SELECT c.customer_name, SUM(o.total_amount) AS total_spend
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_name
ORDER BY total_spend DESC
LIMIT 3;
```

- **`FROM orders o` … `JOIN customers c`** — line up each order with its customer.
  The `o` and `c` are **aliases** (short names) so you can write `o.total_amount`,
  `c.customer_name`.
- **`ON o.customer_id = c.customer_id`** — the join condition: match rows where
  the keys are equal.
- Then the familiar **`GROUP BY` + `SUM`** rolls each customer's orders into a
  total, **`ORDER BY … DESC`** ranks them, and **`LIMIT 3`** keeps the top three.

This is a plain **inner join** — only customers who have orders appear. That's
exactly what you want for "top spenders." This move — join, aggregate, sort,
limit — is the backbone of most analytics queries you'll ever write.

## Your task

Return the **`customer_name`** and **`total_spend`** of the **top 3** customers by
total spend, highest first.
