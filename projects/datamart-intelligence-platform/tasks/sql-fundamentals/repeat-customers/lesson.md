# Filter groups with HAVING

**The scenario.** "Which customers have ordered more than once?" — your repeat
buyers, the people worth a loyalty email. This filters on a *count per group*,
not on individual rows, and that's a job `WHERE` can't do. You need `HAVING`.

## WHERE vs HAVING

The distinction trips up nearly every SQL learner:

- **`WHERE`** filters **rows** — *before* grouping.
- **`HAVING`** filters **groups** — *after* grouping, so it can test an
  aggregate.

```sql
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

1. `GROUP BY customer_id` — one bucket per customer.
2. `COUNT(*)` — how many orders in each bucket.
3. `HAVING COUNT(*) > 1` — keep only buckets with more than one order.

You couldn't write `WHERE COUNT(*) > 1` — at `WHERE` time the groups don't exist
yet. `HAVING` runs *after* aggregation, when the counts are known. Rule of thumb:
if your condition uses an aggregate, it belongs in `HAVING`.

## Your task

Return each **`customer_id`** and its **`order_count`**, keeping only customers
with **more than one** order.
