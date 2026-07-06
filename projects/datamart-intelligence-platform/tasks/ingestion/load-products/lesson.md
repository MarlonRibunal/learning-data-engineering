### Load a raw feed into the warehouse

Source data is rarely clean. The `landing.products_raw` feed has a **duplicate
SKU1** — an older `Widget` and a newer `Widget Pro`. Your job is the first real act
of ingestion: land one clean row per product.

**Your task:** load `raw.products` (`sku`, `name`, `price`) with exactly one row per
`sku`, keeping the **latest** version by `loaded_at`.

Postgres has a neat tool for "one row per group": `DISTINCT ON`.

```
INSERT INTO raw.products (sku, name, price)
SELECT DISTINCT ON (sku) sku, name, price
FROM landing.products_raw
ORDER BY sku, loaded_at DESC;   -- latest per sku wins
```

> Needs the stack: `./platform.sh up` first.
