### Write a data test: no orphan orders

**Referential integrity** means every foreign key points at a real row. An order for
a `customer_id` that doesn't exist is an *orphan* — it breaks joins and inflates
counts. This is exactly what dbt's `relationships` test checks; here you write it by
hand.

**Your task:** return any order whose `customer_id` has no matching row in
`customers`. A `LEFT JOIN` plus `WHERE ... IS NULL` finds the unmatched rows.

```
SELECT o.*
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

> Needs the stack: `./platform.sh up` first.
