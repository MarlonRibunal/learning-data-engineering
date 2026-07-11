# Average per window

**The scenario.** Totals per window show volume; **averages** per window show
*behaviour* — is the typical order getting bigger or smaller over time? Average
order value per 10 minutes is a classic live metric.

## Swap the aggregate

Same windowing you know; just use `avg` instead of `sum`, and round it:

```python
from pyspark.sql import functions as F

events \
    .withColumn("ts", F.to_timestamp("ts")) \
    .groupBy(F.window("ts", "10 minutes")) \
    .agg(F.round(F.avg("amount"), 2).alias("avg_amount"))
```

The windowing API doesn't care which aggregate you apply — `sum`, `avg`, `max`,
`countDistinct` all slot into `.agg(...)` the same way. That interchangeability
is the whole point: learn windowing once, compute any metric over time.

## Your task

Write `transform(events)` returning **`window_start`** (string) and
**`avg_amount`** — the average `amount` in each 10-minute window, rounded to 2.
