# KPI status thresholds

**The scenario.** A number on its own doesn't tell you whether to worry. Is 85%
disk usage fine or a fire? Dashboards answer that by turning a value into a
**status** — the green / amber / red you see on a health tile — using
thresholds.

## The rule

Two thresholds split the range into three bands:

- below `warn` → **`"ok"`** (green)
- at or above `warn`, below `crit` → **`"warn"`** (amber)
- at or above `crit` → **`"critical"`** (red)

The order you check matters: test the **most severe** band first, or a critical
value will match the `warn` condition on the way down.

## Your task

Write `health_status(value, warn, crit)` returning `"ok"`, `"warn"`, or
`"critical"`:

```python
def health_status(value, warn, crit):
    if value >= crit:
        return "critical"
    if value >= warn:
        return "warn"
    return "ok"
```

`health_status(85, 80, 95)` → `"warn"` (past the warn line at 80, not yet
critical at 95).
