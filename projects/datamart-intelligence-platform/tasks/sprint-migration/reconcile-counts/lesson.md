# Reconcile before and after

**Step 3 — the safety net.** The migration ran. Did it move **every** row, and
only those rows? A migration that silently drops 2% of records is worse than one
that crashes — the crash you'd notice. So you **reconcile**: compare row counts
before and after, and surface anything that changed. A clean reconciliation is
what lets you tell downstream teams "it's safe."

## The task

Given `{table: count}` for `before` and `after`, return a dict of the tables
whose count changed, mapping each to its **delta** (`after − before`). Tables
that match are omitted — an empty result means a perfect migration:

```python
def reconcile(before, after):
    return {t: after[t] - before[t] for t in before if after.get(t) != before[t]}
```

`reconcile({"orders": 100, "users": 50}, {"orders": 100, "users": 48})` →
`{"users": -2}` — orders reconciled exactly; users lost 2 rows (a negative delta
you'd chase down before signing off).

## Your task

Write `reconcile(before, after)` in `reconcile.py` returning `{table: delta}` for
every table whose count changed. Empty dict = nothing lost or gained.
