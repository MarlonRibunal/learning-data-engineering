# Distinct counts per window

**The scenario.** Not every metric is a sum. "How many **distinct** products
sold each 10 minutes?", "how many **unique** users were active per minute?" —
these count *distinct* values inside each window, a staple of real-time
engagement metrics.

## The idea

Aggregate the window with `countDistinct` (or `approx_count_distinct` when the
data is huge and an estimate is fine):

```python
from pyspark.sql import functions as F

events \
    .withColumn("ts", F.to_timestamp("ts")) \
    .groupBy(F.window("ts", "10 minutes")) \
    .agg(F.countDistinct("category").alias("categories"))
```

`countDistinct` deduplicates *within each window* before counting — so a window
where category A appears three times still contributes `1` to the distinct
count.

> On a true stream, exact distinct counts require unbounded state (you must
> remember every value seen). That's why production streaming often reaches for
> `approx_count_distinct` (a HyperLogLog sketch) — bounded memory, ~2% error.

## Your task

Write `transform(events)` returning **`window_start`** (string) and
**`categories`** = the number of distinct `category` values in each 10-minute
window.
