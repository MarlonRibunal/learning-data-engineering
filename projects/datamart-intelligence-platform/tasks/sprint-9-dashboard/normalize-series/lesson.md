# Normalize a series for a sparkline

**The scenario.** A sparkline draws a tiny trend in a fixed-height box. To fit
any metric — revenue in the millions, latency in milliseconds — into that box,
you **normalize** it to a `0..1` range first: the smallest value maps to 0
(bottom), the largest to 1 (top), everything else proportionally between.

## Min-max scaling

```
scaled = (value - min) / (max - min)
```

```python
def normalize_series(values):
    lo, hi = min(values), max(values)
    return [round((v - lo) / (hi - lo), 2) for v in values]
```

`normalize_series([10, 20, 30])` → `[0.0, 0.5, 1.0]`. The min pins to 0, the max
to 1, and 20 sits exactly halfway.

## Your task

Write `normalize_series(values)` returning each value min-max scaled to `0..1`,
rounded to 2 decimals.
