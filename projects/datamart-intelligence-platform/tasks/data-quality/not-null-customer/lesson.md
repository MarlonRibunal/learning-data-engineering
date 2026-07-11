# Test: every order has a customer

**The scenario.** An order with no `customer_id` is an orphan — it can't be
attributed to anyone, so it silently vanishes from every per-customer report and
skews your totals. A **not-null** (completeness) test guards the columns that
must always be present.

## The rule

A completeness test returns the rows where a required column is missing:

```sql
SELECT order_id
FROM raw.orders
WHERE customer_id IS NULL;
```

Remember: in SQL, `NULL` is not equal to anything — not even `NULL`. So you must
use `IS NULL`, never `= NULL` (which is always unknown and matches nothing).

On clean data every order has a customer → zero rows. Inject an order with a
`NULL` customer_id → it's returned, and the test fails the batch loudly instead
of letting the orphan through.

## Your task

Write the completeness test in `not_null_customer.sql` — return the `order_id`
of any order missing its `customer_id`. It must catch the injected orphan and
stay quiet on clean data.
