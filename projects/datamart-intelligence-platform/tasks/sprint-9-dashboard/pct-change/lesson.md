# Period-over-period % change

**The scenario.** A KPI tile that just says "Revenue: $120k" is half a story.
The number every stakeholder actually reacts to is the **change**: "▲ 20% vs.
last month." That little delta is what turns a dashboard from a report into a
signal.

## The formula

Percentage change compares a current value to a previous one:

```
(current − previous) / previous × 100
```

- Positive → growth (▲), negative → decline (▽).
- Divide by the **previous** value (the baseline), not the current one — that's
  the classic mistake.
- Round to one decimal so the tile stays clean.

## Your task

Write `pct_change(current, previous)` returning the percentage change from
`previous` to `current`, rounded to **1 decimal place**:

```python
def pct_change(current, previous):
    return round((current - previous) / previous * 100, 1)
```

`pct_change(120, 100)` → `20.0` (revenue grew 20%).

*(In a real dashboard you'd also guard against `previous == 0` to avoid dividing
by zero — worth remembering, though this task's baseline is always non-zero.)*
