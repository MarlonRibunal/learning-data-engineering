# Revenue trend line

A line chart needs points **in order along the x-axis**. Out-of-order points draw a scribble, so the data function has to sort.

## Your task

Write `revenue_by_day(rows)` that returns a list of `{"day": ..., "revenue": ...}` — one entry per day, revenue = the day's total `amount`, **sorted by day ascending**:

```python
def revenue_by_day(rows):
    totals = {}
    for r in rows:
        totals[r["day"]] = totals.get(r["day"], 0) + r["amount"]
    return [{"day": d, "revenue": totals[d]} for d in sorted(totals)]
```

Order matters here — the grader checks the sequence, not just the set.
