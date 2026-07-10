# Conform two sources into one

**The scenario.** The business sells online *and* in physical stores, and each
channel has its own system. The web system emits `web_orders(order_id, amount)`;
the point-of-sale system emits `store_orders(order_id, total)`. They mean the
same thing, but the money column has a different name. Analytics wants **one**
orders table covering every channel — and it needs to know which channel each
order came from.

Combining feeds like this is **conforming**: reshaping each source to a shared
schema so they stack cleanly.

## Two ideas

**1. `UNION ALL` stacks rows.** It glues two result sets top-to-bottom. The
columns line up **by position**, not by name — so you control the shape by how
you write each `SELECT`. (`UNION ALL` keeps every row; plain `UNION` would
dedupe, which you don't want here — different channels can legitimately reuse an
order number.)

**2. Stamp the origin.** Add a literal `source` column to each `SELECT` so a
row's channel is never lost. This is a lineage habit worth keeping for life.

```sql
INSERT INTO raw.orders_all (order_id, amount, source)
SELECT order_id, amount, 'web'   FROM landing.web_orders
UNION ALL
SELECT order_id, total,  'store' FROM landing.store_orders;
```

Look at the second `SELECT`: `total` sits in the `amount` position, so the
store's `total` is conformed onto the shared `amount` column. The literals
`'web'` and `'store'` fill the `source` column.

## Your task

Write the conforming `INSERT` in `conform.sql` so `raw.orders_all` ends up with
all 4 orders — 2 tagged `web`, 2 tagged `store`, totalling 210.
