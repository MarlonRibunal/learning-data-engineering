# Rank within groups (window functions)

**The scenario.** "What's the #1 selling order in *each* category?" A plain
`groupBy` collapses rows — it can't tell you *which* order was the top one,
because it throws the individual rows away. You need to rank rows **within a
group while keeping them**. That's a **window function**.

## How a window works

A window function computes across a set of rows *related to the current row*,
without collapsing them:

```python
from pyspark.sql import functions as F, Window

w = Window.partitionBy("category").orderBy(F.col("amount").desc())
orders.withColumn("rank", F.rank().over(w))
```

- **`partitionBy("category")`** — rank *within* each category, separately.
- **`orderBy(amount desc)`** — biggest amount gets rank 1.
- **`.over(w)`** — apply the window; every row keeps all its columns and gains a
  `rank`.

This is the Spark twin of SQL's `RANK() OVER (PARTITION BY ... ORDER BY ...)` —
you met it in the SQL sprint; here it scales to big data unchanged.

## Your task

Write `transform(orders)` that adds a `rank` (by `amount`, highest = 1, within
each `category`) and returns **`order_id`, `category`, `rank`**:

```python
def transform(orders):
    w = Window.partitionBy("category").orderBy(F.col("amount").desc())
    return (orders.withColumn("rank", F.rank().over(w))
            .select("order_id", "category", "rank"))
```
