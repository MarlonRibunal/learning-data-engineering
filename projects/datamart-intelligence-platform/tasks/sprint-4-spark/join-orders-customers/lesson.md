# Spark: join DataFrames

Real pipelines stitch datasets together. Spark joins two DataFrames on a shared key:

```python
orders.join(customers, on="customer_id").select("order_id", "name", "amount")
```

- **`on="customer_id"`** joins where the key matches (a shared column name avoids duplicate columns).
- The default is an **inner join** — only rows with a match in both sides survive.
- After the join, `.select(...)` picks the columns you want from either side.

Joins are another **shuffle**: Spark co-locates rows with the same key. On big data, a small side can be **broadcast** (`from pyspark.sql.functions import broadcast`) to skip the shuffle — a key optimization, though not required here.

## Your task

Given `orders` (`order_id, customer_id, category, amount`) and `customers` (`customer_id, name`), write `transform(orders, customers)` returning **`order_id`, `name`, `amount`** for each order joined to its customer.
