# Overall status of parallel jobs

**The scenario.** You fanned out one step into several parallel cloud jobs.
Downstream needs a **single** answer: can we proceed? You roll the individual
statuses up with a clear precedence:

- **any** `FAILED` → the whole step `FAILED` (a failure dominates).
- else **any** `RUNNING` → still `RUNNING` (not done yet).
- else → `SUCCESS` (everything finished cleanly).

Order matters: check the most severe state first, so one failure isn't masked by
a bunch of successes.

```python
def overall_status(statuses):
    if "FAILED" in statuses:
        return "FAILED"
    if "RUNNING" in statuses:
        return "RUNNING"
    return "SUCCESS"
```

`overall_status(["SUCCESS", "RUNNING", "SUCCESS"])` → `"RUNNING"` — two done, one
still going, so the step isn't finished.

## Your task

Write `overall_status(statuses)` rolling a list of parallel job states into one,
using the precedence above.
