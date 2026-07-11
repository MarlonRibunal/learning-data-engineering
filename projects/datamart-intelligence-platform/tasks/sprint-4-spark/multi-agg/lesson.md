# Several aggregates at once

**The scenario.** A summary table rarely wants just one number per group — it
wants the count, the total, *and* the average side by side. Spark's `.agg()`
takes as many aggregates as you like in a single pass, so you compute them all
without scanning the data three times.

## Multiple aggregates

```python
from pyspark.sql import functions as F

orders.groupBy("category").agg(
    F.count("*").alias("order_count"),
    F.sum("amount").alias("revenue"),
    F.round(F.avg("amount"), 2).alias("avg_amount"),
)
```

- List each aggregate inside one `.agg(...)`, each with its own `.alias(...)`.
- `F.round(F.avg(...), 2)` rounds the average to cents.
- One `groupBy`, one shuffle — Spark computes all three together.

## Your task

Write `transform(orders)` returning one row per **`category`** with
**`order_count`** (`count`), **`revenue`** (`sum` of amount), and
**`avg_amount`** (`avg` of amount, rounded to 2).
