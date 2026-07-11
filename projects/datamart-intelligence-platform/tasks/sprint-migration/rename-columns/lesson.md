# Map old columns to new

**Step 1 of the migration.** The source used to send `cust` and `amt`; the new
schema wants `customer_id` and `amount`. Before anything downstream can use the
data, you have to **reshape** each record from the old key names to the new — a
rename mapping applied row by row.

## The task

You're given a `mapping` of `{old_name: new_name}`. For each row, rebuild it with
the renamed keys (keeping any key not in the mapping unchanged):

```python
def rename_keys(rows, mapping):
    return [{mapping.get(k, k): v for k, v in row.items()} for row in rows]
```

`mapping.get(k, k)` is the trick: if the key is in the mapping, use the new
name; otherwise fall back to the key itself. That way columns you *didn't* rename
pass through untouched, instead of getting dropped.

`rename_keys([{"cust": 1, "amt": 100}], {"cust": "customer_id", "amt": "amount"})`
→ `[{"customer_id": 1, "amount": 100}]`.

## Your task

Write `rename_keys(rows, mapping)` in `rename_keys.py` — apply the rename to
every row's keys.
