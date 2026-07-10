# Apply a change feed (CDC)

**The scenario.** Your customer records live in an app database you don't own.
Re-copying the whole table every night is slow and wasteful, so instead the
source emits a **change feed** — one row per thing that happened: an insert, an
update, a delete. This is **Change Data Capture (CDC)**, the backbone of modern
ingestion (Debezium, Fivetran, database replication all speak it).

Your job: **apply** those changes to your copy so it matches the source.

## The three operations

Each row in `landing.customer_changes` has an `op`:

| `op` | meaning | what you do |
|------|---------|-------------|
| `I`  | insert  | add the new row |
| `U`  | update  | overwrite the existing row's fields |
| `D`  | delete  | mark it gone — **don't physically remove it** |

Inserts and updates are the same operation against a table with a primary key:
an **upsert**. Handle both at once with `ON CONFLICT`.

Deletes are special. In a warehouse you almost never hard-delete — you **soft
delete** by setting an `is_deleted` flag. That preserves history (you can still
report on what a customer bought before they closed their account) and keeps
downstream joins stable.

## Step by step

**1. Upsert the inserts and updates:**

```sql
INSERT INTO raw.customers_cdc (customer_id, name, is_deleted)
SELECT customer_id, name, false
FROM landing.customer_changes
WHERE op IN ('I', 'U')
ON CONFLICT (customer_id) DO UPDATE
    SET name = EXCLUDED.name, is_deleted = false;
```

`ON CONFLICT ... DO UPDATE` means "insert if new, otherwise update the existing
row." `EXCLUDED` refers to the row you tried to insert.

**2. Soft-delete the deletes:**

```sql
UPDATE raw.customers_cdc
SET is_deleted = true
WHERE customer_id IN (
    SELECT customer_id FROM landing.customer_changes WHERE op = 'D'
);
```

## Your task

Write both statements in `cdc_apply.sql`. Afterward: customer 10 is renamed to
"Ana Smith", customer 12 exists, and customer 11 is still present but flagged
`is_deleted = true`.
