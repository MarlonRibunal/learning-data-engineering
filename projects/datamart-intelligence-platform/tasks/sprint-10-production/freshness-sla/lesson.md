# Freshness SLAs

The worst way to learn your pipeline broke is a stakeholder asking why the
dashboard is a day stale. Production data has a **freshness SLA** — a max age
it's allowed to reach — and a monitor that flags anything past it, so *you*
find out first.

## Your task

Write `stale_tables(tables, max_age_min)` where `tables` is a list of
`{"name": ..., "age_min": ...}` (minutes since last update). Return the
**names** of tables older than `max_age_min`, **sorted**:

```python
def stale_tables(tables, max_age_min):
    return sorted(t["name"] for t in tables if t["age_min"] > max_age_min)
```

With a 60-minute SLA, a table updated 120 minutes ago is stale; one updated
5 minutes ago is fine.
