# Verify the recovery

**Step 4 — the one people skip.** The backfill ran without errors. That does
**not** mean the data is correct. Before you close the incident, reconcile the
actual row counts against what you *expected* — a job can succeed and still write
the wrong number of rows. Skipping this step is how a "resolved" incident quietly
reopens the next morning.

## The task

You have two dicts of `{table: row_count}` — `expected` (what should be there)
and `actual` (what's there now). Return the **sorted names** of the tables that
still don't match:

```python
def unrecovered(expected, actual):
    return sorted(name for name in expected if actual.get(name) != expected[name])
```

Use `actual.get(name)` (not `actual[name]`) so a table missing entirely from
`actual` counts as unrecovered instead of crashing — a table that vanished is the
*worst* case, not one to blow up on.

`unrecovered({"orders": 100, "users": 50}, {"orders": 100, "users": 48})` →
`["users"]` — orders reconciled, users is still short.

## Your task

Write `unrecovered(expected, actual)` in `verify.py` returning the sorted names of
tables whose actual count doesn't match expected. An empty list means you can
close the incident.
