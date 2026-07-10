# Spark: select and filter

The two most fundamental DataFrame operations:

- **`.filter(condition)`** keeps only the rows that match (like SQL `WHERE`).
- **`.select("col", ...)`** keeps only the columns you name (like SQL `SELECT`).

Both are **transformations** — Spark records them lazily and only does the work when an *action* (like `.collect()`) runs. That laziness is what lets Spark optimize and scale.

## Your task

You're given an `orders` DataFrame with columns `order_id, customer_id, category, amount`.

Write `transform(orders)` that returns **only `order_id` and `amount`**, for orders with **`amount` of at least 50**.

```python
def transform(orders):
    return orders.filter(orders.amount >= 50).select("order_id", "amount")
```

Column references can be `orders.amount`, `orders["amount"]`, or (with `from pyspark.sql import functions as F`) `F.col("amount")`.
