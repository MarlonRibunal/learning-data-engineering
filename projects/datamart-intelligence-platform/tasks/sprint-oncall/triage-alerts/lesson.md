# Triage the freshness alerts

**Step 1 of the incident.** Your monitoring reports the age (minutes since last
update) of every table. Before you fix anything, figure out **which tables are
actually breached** — chasing a table that's 5 minutes old when your SLA is 60
just wastes precious incident time.

## The task

You have a freshness SLA (max allowed age, in minutes). Return the **names** of
the tables that exceed it, **sorted** so your incident notes are tidy:

```python
def stale_tables(tables, sla_minutes):
    return sorted(t["name"] for t in tables if t["age_min"] > sla_minutes)
```

`tables` is a list of `{"name": ..., "age_min": ...}`. With a 60-minute SLA, the
5-minute-old `orders` is fine; `payments` (90) and `users` (200) are breached.

## Your task

Write `stale_tables(tables, sla_minutes)` in `triage.py` — return the sorted
names of every table older than the SLA. Those are the ones your incident is
actually about.
