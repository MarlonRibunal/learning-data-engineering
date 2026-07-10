# Group by window *and* a dimension

**The scenario.** "Revenue per 10 minutes" is useful; "revenue per 10 minutes
**per category**" is what a real live dashboard shows — one line per product
category, each ticking up over time. That means grouping by **two** keys at
once: the time window *and* the dimension.

## The idea

`groupBy` takes as many keys as you like. Put the window first, then the
dimension:

```python
from pyspark.sql import functions as F

events \
    .withColumn("ts", F.to_timestamp("ts")) \
    .groupBy(F.window("ts", "10 minutes"), "category") \
    .agg(F.sum("amount").alias("revenue"))
```

Now each output row is one (window, category) pair with its own total. A window
with two active categories produces two rows; that's exactly what you want for a
multi-series chart.

## Your task

Write `transform(events)` (`ts` string, `category`, `amount`) returning
**`window_start`** (string), **`category`**, and **`revenue`** (sum of `amount`)
for each 10-minute window / category combination:

```python
def transform(events):
    return (events.withColumn("ts", F.to_timestamp("ts"))
            .groupBy(F.window("ts", "10 minutes"), "category")
            .agg(F.sum("amount").alias("revenue"))
            .select(F.col("window.start").cast("string").alias("window_start"),
                    "category", "revenue"))
```
