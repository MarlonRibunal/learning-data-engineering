# Bronze to silver (medallion architecture)

**The scenario.** Databricks popularized the **medallion architecture** — a
three-layer refinement of data in a lakehouse:

- **Bronze** — raw, as-ingested. Immutable, messy, complete (your landing zone).
- **Silver** — cleaned and conformed: deduplicated, validated, typed. The
  trustworthy base everyone builds on.
- **Gold** — business-level aggregates and marts, ready for BI.

It's the same "raw → staging → marts" idea from dbt, given catchy names and a
lakehouse home. This level builds the **bronze → silver** step, where the real
data-quality work happens.

## The task

Refine bronze into silver: **deduplicate** by key (keep the latest) and **drop
invalid rows** (here, a null `value`):

```python
def to_silver(bronze):
    latest = {}
    for row in bronze:
        latest[row["id"]] = row          # last write wins — dedup
    return [latest[k] for k in sorted(latest) if latest[k]["value"] is not None]
```

Two duplicate `id=1` rows collapse to the latest (`value="b"`); the `id=2` row
with a null value is dropped. That's silver: fewer rows, all trustworthy.

## Your task

Write `to_silver(bronze)` returning the deduplicated (latest-per-`id`), non-null
rows, sorted by `id`.
