# Smooth a line with a moving average

**The scenario.** A raw daily-revenue line is jagged — weekends dip, one big
order spikes it. A **moving average** smooths that noise so the *trend* is
readable: each point becomes the average of itself and the previous few.

## Trailing window

A trailing moving average of window `w` averages the current point and the
`w-1` before it. At the very start there aren't `w` points yet, so you average
whatever is available:

```python
def moving_average(values, w):
    out = []
    for i in range(len(values)):
        window = values[max(0, i - w + 1) : i + 1]
        out.append(round(sum(window) / len(window), 2))
    return out
```

`moving_average([10, 20, 30, 40], 2)` → `[10.0, 15.0, 25.0, 35.0]` — the first
point is just `10` (no prior), then each is the mean of two.

## Your task

Write `moving_average(values, w)` returning the trailing moving average (window
`w`), each rounded to 2 decimals.
