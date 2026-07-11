# Time travel

**The scenario.** Because Delta Lake keeps a **transaction log** of every commit,
it can reconstruct the table **as it was at any past version** — "time travel."
`SELECT * FROM orders VERSION AS OF 42` (or `TIMESTAMP AS OF '2026-03-01'`) is a
real query. It's the lakehouse superpower for auditing, debugging ("what did the
data look like before that bad load?"), reproducing a report, and rolling back a
mistake.

It's the same idea as the snapshots you built in Architecture — but *automatic*:
you don't build snapshot tables, the transaction log gives you every version for
free.

## The task

Given a table's version history (each entry is that version's rows) and a target
version number, return the table as of that version:

```python
def snapshot_at(history, version):
    return history[version]
```

With commits `[[1], [1,2], [1,2,3]]`, version `1` is `[1, 2]` — the table's state
after the second commit, ignoring the later insert of `3`.

## Your task

Write `snapshot_at(history, version)` returning the rows at the given version —
the lakehouse reading its own past.
