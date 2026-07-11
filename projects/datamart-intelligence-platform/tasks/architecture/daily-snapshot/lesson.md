# Daily snapshot table

**The scenario.** Orders change status over time — `pending` today, `shipped`
tomorrow. A raw table only shows the *current* state, so you can never answer
"how many orders were still pending **as of last Tuesday**?" A **snapshot table**
fixes that: each day you append a full copy of the current state, stamped with a
`snapshot_date`. Over time it becomes a flip-book of history you can query at any
point in time.

## The pattern

Insert *all* current rows, tagging each with the snapshot's date:

```sql
INSERT INTO analytics.orders_snapshot (snapshot_date, order_id, status, total_amount)
SELECT DATE '2026-03-01', order_id, status, total_amount
FROM raw.orders;
```

Two things make it a snapshot:

- **Every row**, not a filtered subset — a snapshot is a complete as-of picture.
- **One `snapshot_date`** stamped on all of them — that literal date is the "when"
  you'll later filter on (`WHERE snapshot_date = '...'`).

Run it again tomorrow with a new date and yesterday's rows stay untouched — that
accumulation is the whole point.

## Your task

Populate `analytics.orders_snapshot` with **all 5** orders from `raw.orders`,
each stamped with `snapshot_date = 2026-03-01`.
