# Test: emails are unique

**The scenario.** Your `customers` table has a primary key on `customer_id`, so
*that* can't duplicate. But `email` has no such guarantee — and a duplicate
email usually means the same person was signed up twice, which quietly
double-counts them in every "customers who…" report. A **uniqueness test** on a
non-key column catches it.

## How a data test works (recap)

A data test is a query that **returns the rows that break the rule**. It
*passes* when it returns **zero** rows. The grader runs yours twice:

- against **clean** data → it must return nothing (no false alarms),
- against **dirty** data (a duplicate email injected) → it must return the
  offender.

## Finding duplicates

Group by the column and keep only groups that appear more than once:

```sql
SELECT email
FROM raw.customers
GROUP BY email
HAVING COUNT(*) > 1;
```

On clean data every email is unique, so every group has count 1 and `HAVING`
filters them all out → zero rows. Inject a second `ada@example.com` and that
group's count becomes 2 → it's returned.

## Your task

Write the uniqueness test in `unique_email.sql`. It must flag the duplicated
email on dirty data and stay silent on clean data.
