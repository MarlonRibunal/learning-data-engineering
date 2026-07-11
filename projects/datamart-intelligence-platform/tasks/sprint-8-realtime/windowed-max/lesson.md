# Biggest order per window

**The scenario.** Spikes matter. "What was the single largest order in each
10-minute window?" flags outliers and surge moments a sum would hide — a fraud
signal, a flash-sale spike, a runaway retry. `max` per window surfaces them.

## Max as the aggregate

```python
from pyspark.sql import functions as F

events \
    .withColumn("ts", F.to_timestamp("ts")) \
    .groupBy(F.window("ts", "10 minutes")) \
    .agg(F.max("amount").alias("max_amount"))
```

Same shape as every other windowed metric — `F.max` returns the largest value in
each window. (Its twin `F.min` gives the smallest.)

## Your task

Write `transform(events)` returning **`window_start`** (string) and
**`max_amount`** — the largest `amount` in each 10-minute window.
