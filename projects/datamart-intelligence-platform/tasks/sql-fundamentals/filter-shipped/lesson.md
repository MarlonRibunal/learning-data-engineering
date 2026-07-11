# Filter rows with WHERE

**The scenario.** You rarely want *all* the rows — you want the ones that matter:
the shipped orders, the paying customers, today's events. The `WHERE` clause is
how SQL keeps only the rows that match a condition.

## How WHERE works

`WHERE` sits after `FROM` and tests each row; only rows where the condition is
**true** come back:

```sql
SELECT *
FROM orders
WHERE status = 'shipped';
```

- **`=`** tests equality. Text values go in **single quotes** (`'shipped'`), not
  double quotes — a classic beginner trip-up.
- Other comparisons: `<`, `>`, `<=`, `>=`, `<>` (not equal), plus `IN (...)`,
  `BETWEEN`, and `LIKE` for pattern matching.
- Combine conditions with `AND` / `OR`.

Think of `WHERE` as a sieve applied row by row, before any grouping or sorting
happens.

## `SELECT *` here

This task uses `SELECT *` because you want the *whole* shipped order, every
column — a case where `*` is genuinely what you mean.

## Your task

Return **every column** of the orders whose `status` is `'shipped'`.

```sql
SELECT *
FROM orders
WHERE status = 'shipped';
```
