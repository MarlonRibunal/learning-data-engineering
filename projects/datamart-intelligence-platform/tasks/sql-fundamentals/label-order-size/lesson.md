# Conditional logic with CASE

**The scenario.** Raw numbers are hard to skim. A dashboard reads better with
labels — is this a "large" or "small" order? **`CASE`** is SQL's if/then: it
turns a value into a category on the fly, without changing the underlying data.

## CASE expression

```sql
SELECT order_id,
       CASE WHEN total_amount >= 100 THEN 'large' ELSE 'small' END AS order_size
FROM orders;
```

- **`CASE WHEN <condition> THEN <value>`** — if the condition is true, use this
  value.
- **`ELSE <value>`** — the fallback for everything that didn't match.
- **`END`** — closes the `CASE`; **`AS order_size`** names the new column.

You can chain multiple `WHEN`s for more buckets (`WHEN ... THEN 'huge' WHEN ...
THEN 'large' ELSE 'small'`) — they're tested top to bottom, first match wins.
`CASE` is one of the most-used tools in analytics SQL: bucketing, relabeling, and
conditional sums (`SUM(CASE WHEN ... THEN 1 ELSE 0 END)`) all lean on it.

## Your task

Return each **`order_id`** and an **`order_size`** label: `'large'` when
`total_amount` is **100 or more**, otherwise `'small'`.
