# Spark: group and aggregate

Rolling many rows up into a summary is the heart of analytics. In Spark:

```python
from pyspark.sql import functions as F

df.groupBy("category").agg(F.sum("amount").alias("revenue"))
```

- **`.groupBy("col")`** buckets rows by a key.
- **`.agg(F.sum(...), F.count(...), ...)`** computes one value per bucket.
- **`.alias("name")`** names the output column — do this so the result column is exactly what's expected.

Under the hood a `groupBy` triggers a **shuffle**: Spark moves rows across the cluster so all rows for a key land together. It's the expensive-but-powerful step that makes distributed aggregation possible.

## Your task

Given `orders` (`order_id, customer_id, category, amount`), write `transform(orders)` returning one row per **`category`** with a **`revenue`** column = the sum of `amount`.
