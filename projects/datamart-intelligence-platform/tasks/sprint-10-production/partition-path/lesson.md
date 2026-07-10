# Build a partition path

**The scenario.** You're writing daily data to a data lake (S3, GCS, HDFS).
Dump everything into one folder and every query scans everything — slow and
expensive. Instead you **partition** by date, laying files out so a query for
"March 1st" reads only that day's folder. The layout is a convention, and
getting the format exactly right matters — a typo means the query engine can't
prune, or worse, silently reads nothing.

## The convention (Hive-style)

Partition folders are `key=value`, nested from coarse to fine:

```
orders/year=2026/month=03/day=01/
```

Engines like Spark, Athena, and BigQuery read this and skip every folder that
can't match the filter. The zero-padding (`03`, not `3`) keeps folders sorted
and consistent — don't drop it.

## Your task

Write `partition_path(table, date)` where `date` is an ISO string
`"YYYY-MM-DD"`. Return the partition path:

```python
def partition_path(table, date):
    year, month, day = date.split("-")
    return f"{table}/year={year}/month={month}/day={day}"
```

`partition_path("orders", "2026-03-01")` →
`"orders/year=2026/month=03/day=01"`. Splitting the ISO string keeps the
zero-padding for free.
