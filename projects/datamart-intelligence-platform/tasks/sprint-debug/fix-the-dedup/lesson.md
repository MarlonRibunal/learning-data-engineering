# Bug report: stale records on the dashboard

> "Customer 1 updated their record, but the dashboard still shows the **old**
> value. The dedup step is keeping the wrong version."

## The buggy code

```python
def dedupe_latest(events, key):
    best = {}
    for e in events:
        if e[key] not in best:      # <-- only stores the FIRST time it sees a key
            best[e[key]] = e
    return [best[k] for k in sorted(best)]
```

Trace it: the first `id=1` (version 1) gets stored; the second `id=1` (version 2,
the *newer* one) is skipped because `id=1` is already in `best`. So it keeps the
**oldest** version — the exact opposite of "latest."

## The fix

Replace the "only if unseen" rule with "keep the higher version":

```python
def dedupe_latest(events, key):
    best = {}
    for e in events:
        if e[key] not in best or e["version"] > best[e[key]]["version"]:
            best[e[key]] = e
    return [best[k] for k in sorted(best)]
```

## Your task

Fix `dedupe_latest` in `dedupe_latest.py` so it keeps the **highest `version`**
per key. Expected: customer 1 keeps version 2 (`v = "b"`).
