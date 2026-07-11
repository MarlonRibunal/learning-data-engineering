# Find the root-cause job

**Step 2 of the incident.** Your pipeline is a chain: `extract → transform →
load`. When `transform` fails, `load` fails too — but `load` isn't broken, it's a
**victim**. Fixing victims wastes time; you have to find the **first** failure in
the chain, because that's the one that actually needs your attention.

## The task

The job runs come in execution order. Walk them and return the name of the
**first** one whose status is `failed`:

```python
def first_failure(runs):
    for run in runs:
        if run["status"] == "failed":
            return run["job"]
    return None
```

Order matters here — that's why you scan front-to-back and return on the *first*
failure. Everything after it is collateral damage.

## Your task

Write `first_failure(runs)` in `root_cause.py`. `runs` is a list of
`{"job": ..., "status": ...}` in execution order. Return the name of the first
failed job (the root cause), or `None` if nothing failed.
