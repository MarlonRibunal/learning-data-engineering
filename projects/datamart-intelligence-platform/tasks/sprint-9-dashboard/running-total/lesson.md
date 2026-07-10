# Running total

**The scenario.** "How much revenue have we booked *so far* this month?" A
daily bar chart answers "how much each day"; a **running total** (cumulative
sum) answers "how much to date" — the line that climbs left to right toward a
goal. It's one of the most-requested dashboard shapes.

## The idea

Walk the values in order, keeping a running sum, and emit the sum after each
step:

```
[100, 20, 30]  →  [100, 120, 150]
 100            (100)
      +20       (120)
          +30   (150)
```

Each output point is "everything up to and including here."

## Your task

Write `running_total(values)` that returns the cumulative sums, in order:

```python
def running_total(values):
    out, total = [], 0
    for v in values:
        total += v
        out.append(total)
    return out
```

Order matters — the grader checks the sequence. Don't sort or reorder; a
running total only makes sense along the existing order (usually time).
