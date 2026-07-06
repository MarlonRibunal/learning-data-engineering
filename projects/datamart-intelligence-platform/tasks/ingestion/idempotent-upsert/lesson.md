### Idempotency: make a load safe to re-run

Pipelines re-run — on a schedule, after a failure, during a backfill. A load that
breaks (or duplicates data) the second time it runs is a production incident waiting
to happen. A load you can run any number of times with the same result is
**idempotent**, and it's one of the most important habits in data engineering.

The scaffold's plain `INSERT` works once, then fails with a duplicate-key error on
the re-run. Fix it with an **upsert** — insert, or update the row if the key already
exists:

```
INSERT INTO raw.products (sku, name, price)
SELECT DISTINCT ON (sku) sku, name, price
FROM landing.products_raw
ORDER BY sku, loaded_at DESC
ON CONFLICT (sku) DO UPDATE
    SET name = EXCLUDED.name, price = EXCLUDED.price;
```

The grader runs your load **twice** — a correct upsert leaves exactly 3 rows.

> Needs the stack: `./platform.sh up` first.
