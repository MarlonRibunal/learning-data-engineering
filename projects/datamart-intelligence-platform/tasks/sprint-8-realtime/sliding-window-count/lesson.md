# Sliding windows

A **tumbling** window updates once per window length — a 10-minute window gives you a fresh number every 10 minutes. Often you want smoother, more frequent updates: a **sliding window** is a fixed-width window that advances by a smaller *slide* interval, so windows **overlap** and each event falls into several.

```python
from pyspark.sql import functions as F

events \
    .withColumn("ts", F.to_timestamp("ts")) \
    .groupBy(F.window("ts", "10 minutes", "5 minutes")) \
    .count()
```

The third argument is the **slide duration**. `window("ts", "10 minutes", "5 minutes")` = a 10-minute window that starts every 5 minutes (…08:55, 09:00, 09:05…). This powers "last 10 minutes, refreshed every 5" style live metrics.

## Your task

Given `events` (`ts` string, `category`, `amount`), write `transform(events)` returning **`window_start`** (string) and **`count`** for a **10-minute window sliding every 5 minutes**.
