### Select specific columns

The most basic SQL question: *"show me these columns from this table."*

**Your task:** return `order_id`, `status`, and `total_amount` for every order.
Name the columns explicitly rather than using `SELECT *` — real queries almost
always ask for exactly the columns they need.

```
SELECT column_a, column_b
FROM table_name;
```

The `orders` table has: `order_id`, `customer_id`, `order_date`, `total_amount`, `status`.
