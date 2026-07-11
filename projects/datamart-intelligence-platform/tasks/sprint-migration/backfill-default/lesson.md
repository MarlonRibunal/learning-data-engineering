# Backfill a new column

**Step 2 of the migration.** The new schema adds a `region` column. Some records
already carry it (they came from a newer source), but the historical rows don't.
You need to **backfill** a default for the ones that are missing it — **without
overwriting** the rows that already have a real value. Clobbering existing data
is the classic backfill disaster.

## The task

For each row, ensure the column exists: keep the row's value if it's already
there, otherwise fill the default:

```python
def add_column(rows, column, default):
    return [{**row, column: row.get(column, default)} for row in rows]
```

The key is `row.get(column, default)` **inside** the spread `{**row, ...}`:
`{**row}` copies the row, then the explicit `column:` sets it — but to
`row.get(column, default)`, which is the *existing* value when present and the
default only when absent. Reversing that (writing `default` unconditionally)
would wipe real data — the exact bug this pattern avoids.

`add_column([{"id": 1}, {"id": 2, "region": "US"}], "region", "UNKNOWN")` →
`[{"id": 1, "region": "UNKNOWN"}, {"id": 2, "region": "US"}]` — row 1 gets the
default, row 2 keeps `US`.

## Your task

Write `add_column(rows, column, default)` in `add_column.py` — add the column
with the default only where it's missing.
