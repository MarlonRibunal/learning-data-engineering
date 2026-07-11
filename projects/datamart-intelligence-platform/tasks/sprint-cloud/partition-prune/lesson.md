# Partition pruning

**The scenario.** You now know cloud warehouses bill by bytes scanned. **Partition
pruning** is the single biggest lever to scan less: if a table is partitioned by
date, a query filtered to a date range reads **only** the matching partitions and
skips the rest — often turning a full-table scan (and its bill) into a sliver.

It's the same idea as the data-lake partition paths from the Production sprint,
now seen from the *query* side: the engine looks at your `WHERE date BETWEEN ...`
and eliminates partitions that can't match before reading a single byte.

## The task

Given a table's partition keys (dates) and a `[start, end]` filter range, return
the partitions that would actually be scanned — those inside the range, sorted:

```python
def pruned(partitions, start, end):
    return sorted(p for p in partitions if start <= p <= end)
```

With partitions for Mar 1–4 and a filter of Mar 2–3, only `["2026-03-02",
"2026-03-03"]` are read; Mar 1 and Mar 4 are pruned (and never billed).

## Your task

Write `pruned(partitions, start, end)` returning the sorted partitions within the
inclusive range. This is what makes a partitioned cloud table cheap to query — and
an unpartitioned one expensive.
