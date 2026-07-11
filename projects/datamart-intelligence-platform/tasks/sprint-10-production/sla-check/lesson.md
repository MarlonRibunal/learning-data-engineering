# Did we meet the latency SLA?

**The scenario.** Your SLA promises results within 200 ms. A run took 120 ms — a
pass. The check itself is trivial, but SLAs live or die on the **boundary**: is
*exactly* 200 ms a pass or a fail? Decide it explicitly and consistently, because
that one `<` vs `<=` is the difference between "met" and "breached" on the
threshold.

## The task

Treat "at or under target" as meeting the SLA (`<=`):

```python
def sla_met(actual_ms, target_ms):
    return actual_ms <= target_ms
```

`sla_met(120, 200)` → `True`. Returning a real boolean (not `"yes"`/`1`) keeps it
composable with the rest of your alerting logic.

## Your task

Write `sla_met(actual_ms, target_ms)` returning `True` when the actual latency is
at or under the target, else `False`.
