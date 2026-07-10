# Quarantine the bad rows (dead-letter pattern)

**The scenario.** Your order feed comes from an upstream service you don't
control. Most rows are fine, but every day a few are broken — a checkout bug
sends an order with no `customer_id`, a refund arrives as a negative `amount`.
You have two bad options and one good one:

- ❌ **Let bad rows in** → they poison every downstream report.
- ❌ **Fail the whole load** → one bad row blocks thousands of good ones.
- ✅ **Quarantine** → load the good rows now, set the bad ones aside (with a
  reason) so someone can investigate. This is the **dead-letter** pattern, and
  it's how resilient ingestion actually works.

## What "bad" means here

A row is invalid if it has **no `customer_id`** (`customer_id IS NULL`) or a
**negative `amount`** (`amount < 0`). Everything else is clean.

## Step by step

**1. Load the clean rows** into `raw.orders_clean` — the good ones only:

```sql
INSERT INTO raw.orders_clean (order_id, customer_id, amount)
SELECT order_id, customer_id, amount
FROM landing.orders_raw
WHERE customer_id IS NOT NULL AND amount >= 0;
```

**2. Quarantine the rest** into `raw.orders_quarantine`, tagging *why* each was
rejected — a `reason` is what makes a dead-letter table actionable:

```sql
INSERT INTO raw.orders_quarantine (order_id, customer_id, amount, reason)
SELECT order_id, customer_id, amount,
       CASE WHEN customer_id IS NULL THEN 'missing customer_id'
            WHEN amount < 0        THEN 'negative amount'
       END
FROM landing.orders_raw
WHERE customer_id IS NULL OR amount < 0;
```

Notice the two `WHERE` clauses are exact opposites — together they cover every
row exactly once, so nothing is lost and nothing is double-counted.

## Your task

Write both `INSERT`s in `quarantine.sql`. When you're done, `orders_clean` holds
the 2 good rows (total 130) and `orders_quarantine` holds the 2 bad ones.
