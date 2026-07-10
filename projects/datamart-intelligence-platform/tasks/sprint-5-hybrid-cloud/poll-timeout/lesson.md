# Stop polling at a timeout

**The scenario.** A poll loop that waits *forever* is a landmine — if the remote
job hangs, your pipeline hangs with it, holding a worker and never alerting. Two
rules make polling safe:

1. **Stop at the first terminal state** — don't keep polling (or, worse, read a
   later value) once the run is done.
2. **Cap the attempts** — after `max_polls` checks with no result, give up with
   a `TIMEOUT` so the pipeline fails fast instead of hanging.

## Your task

`poll_result(statuses, max_polls)` receives the sequence of statuses successive
polls would return. Return the **first terminal** status seen within the first
`max_polls` polls; if none is terminal in that budget, return `"TIMEOUT"`:

```python
TERMINAL = {"SUCCESS", "FAILED", "CANCELED"}

def poll_result(statuses, max_polls):
    for i, status in enumerate(statuses):
        if i >= max_polls:
            break
        if status in TERMINAL:
            return status
    return "TIMEOUT"
```

`poll_result(["RUNNING", "SUCCESS", "FAILED"], 5)` → `"SUCCESS"` — it stops at
the first terminal state and never reaches the later `FAILED`. That "stop early"
detail is exactly what a naive `return statuses[-1]` gets wrong.
