# Test: order dates are plausible

**The scenario.** A bug or a bad manual entry stamps an order with
`order_date = 2099-01-01`. Nothing is `NULL`, nothing is duplicated — the row
looks fine to a not-null or uniqueness test. But a single far-future date can
wreck a time-series chart (the x-axis suddenly stretches to the year 2099) and
break "revenue this month" math. A **range / plausibility** test catches values
that are *technically valid but obviously wrong*.

## The rule

Pick a sane window for the column and return anything outside it. Orders can't
predate the business or come from the far future:

```sql
SELECT order_id
FROM raw.orders
WHERE order_date < DATE '2020-01-01'
   OR order_date > DATE '2030-01-01';
```

The `DATE '...'` literal makes the comparison unambiguous. On clean data every
order sits in 2026 → zero rows. The injected `2099` order falls outside the
upper bound → it's flagged.

## Your task

Write the plausibility test in `plausible_dates.sql` — return the `order_id` of
any order dated before 2020 or after 2030. Catch the future-dated order without
flagging the real ones.
