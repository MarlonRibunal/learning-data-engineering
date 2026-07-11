# Error rate

**The scenario.** A pipeline processed 200 records and 10 failed. "10 failures"
sounds alarming on its own, but as a **rate** — 5% — you can compare it against
your error budget and decide whether to page someone. Rates, not raw counts, are
what alerting thresholds are built on.

## The task

```python
def error_rate(total, failed):
    return round(failed / total * 100, 1)
```

`error_rate(200, 10)` → `5.0`. Divide failures by the **total** (not by
successes), times 100 for a percentage, rounded to one decimal.

## Your task

Write `error_rate(total, failed)` returning the failure percentage rounded to
one decimal.
