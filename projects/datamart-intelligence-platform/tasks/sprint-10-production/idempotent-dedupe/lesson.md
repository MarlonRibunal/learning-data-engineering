# Idempotent de-duplication

A pipeline that runs twice — a retry, a backfill, a replayed stream — must produce the **same** result as running once. That property is **idempotency**, and the most common way to lose it is double-counting duplicate records.

The fix: collapse duplicates by a key, keeping the **latest** version (a last-write-wins upsert).

## Your task

Write `dedupe(events, key)` where `events` is a list of dicts. Return the deduplicated events — for each distinct value of `key`, keep the **last** occurrence — **sorted by the key**:

```python
def dedupe(events, key):
    last = {}
    for e in events:
        last[e[key]] = e       # later records overwrite earlier ones
    return [last[k] for k in sorted(last)]
```
