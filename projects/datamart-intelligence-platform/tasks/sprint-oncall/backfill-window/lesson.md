# Compute the backfill window

**Step 3 of the incident.** You fixed the broken job. Now you have to
**backfill** the days it missed — recompute them so the data is whole again. The
danger is the boundaries: reprocess one day too few and you leave a gap;
reprocess `last_success` again and you might double-count. You want *exactly* the
days after the last good run, up to and including today.

## The task

Given the `last_success` date and `today` (ISO strings), return the list of dates
to reprocess — **the day after `last_success` through `today`, inclusive**:

```python
from datetime import date, timedelta

def backfill_dates(last_success, today):
    start = date.fromisoformat(last_success) + timedelta(days=1)
    end = date.fromisoformat(today)
    out, d = [], start
    while d <= end:
        out.append(d.isoformat())
        d += timedelta(days=1)
    return out
```

- **`+ timedelta(days=1)`** on the start — `last_success` already ran, so skip it
  (this is the "no double-count" boundary).
- **`<= end`** — include today (the "no gap" boundary).

`backfill_dates("2026-03-01", "2026-03-04")` →
`["2026-03-02", "2026-03-03", "2026-03-04"]`.

## Your task

Write `backfill_dates(last_success, today)` in `backfill.py` returning the ISO
date strings to reprocess — every missing day, and only the missing days.
