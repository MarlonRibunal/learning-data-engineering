# MERGE — upsert on the lakehouse

**The scenario.** Plain object storage (S3, GCS) has no transactions — you can't
safely update a file while others read it. **Delta Lake** (and Iceberg, Hudi)
add an ACID transaction log *over* those files, giving the data lake
database-grade guarantees. The signature operation that unlocks is **`MERGE`**:
upsert a batch of changes into a table atomically.

`MERGE INTO target USING updates ON target.id = updates.id WHEN MATCHED THEN
UPDATE WHEN NOT MATCHED THEN INSERT` — one statement that updates existing rows
and inserts new ones, transactionally. It's how the lakehouse applies CDC feeds,
SCDs, and incremental loads (all the patterns you drilled in Ingestion) directly
on cheap storage.

## The task

Implement the merge logic: for each update, replace the matching target row by
key, or add it if new. Return the result sorted by key:

```python
def merge(target, updates, key):
    by_key = {row[key]: row for row in target}
    for update in updates:
        by_key[update[key]] = update      # matched -> update; new -> insert
    return [by_key[k] for k in sorted(by_key)]
```

`id=2` is updated to `v="B"`, `id=3` is inserted, `id=1` is untouched.

## Your task

Write `merge(target, updates, key)` performing the upsert (update matches, insert
new), returned sorted by `key`.
