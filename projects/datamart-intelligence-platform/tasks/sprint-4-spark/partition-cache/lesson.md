# Spark: repartition and cache

Two levers that decide how fast a Spark job runs:

- **`.repartition(n)`** splits the data into `n` partitions — the unit of parallelism. More partitions = more tasks Spark can run at once across the cluster. Too few and cores sit idle; too many and overhead dominates.
- **`.cache()`** keeps a DataFrame in memory after it's first computed, so reusing it doesn't recompute the whole lineage. Essential when you branch off the same intermediate result many times.

```python
df.repartition(4).cache()
```

`cache()` is lazy — it marks the DataFrame to be cached the next time an action runs.

## Your task

Given `orders`, write `transform(orders)` that returns just **`order_id` and `amount`**, spread across **4 partitions** and **cached**.

```python
def transform(orders):
    return orders.select("order_id", "amount").repartition(4).cache()
```
