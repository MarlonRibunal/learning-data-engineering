# Circuit breaker

**The scenario.** A downstream service is down. Your pipeline keeps calling it,
each call waiting for a timeout, piling up load on something already broken —
and wasting your run's time. A **circuit breaker** stops the bleeding: after
enough consecutive failures it "trips **open**" and fails fast, so you stop
hammering a dead service and can alert instead. Once things recover, it closes
again.

This is the same idea as the breaker in your house: too much current, it flips,
everything downstream stops until you reset it.

## The rule

Look at the most recent results. Count the **consecutive** failures at the end
(the current streak). If that streak reaches the `threshold`, the breaker is
**`"open"`**; otherwise it's **`"closed"`**. A single success resets the streak
— that's why you count from the end, not the whole history.

## Your task

Write `circuit_state(results, threshold)` where `results` is a list of
`"ok"`/`"fail"` (oldest first). Return `"open"` or `"closed"`:

```python
def circuit_state(results, threshold):
    streak = 0
    for r in reversed(results):
        if r == "fail":
            streak += 1
        else:
            break
    return "open" if streak >= threshold else "closed"
```

`circuit_state(["ok", "fail", "fail", "fail"], 3)` → `"open"` — three failures
in a row, trip it.
