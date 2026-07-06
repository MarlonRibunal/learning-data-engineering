### Write a data test: no negative amounts

A **data test** is a query that returns the rows that *break a rule*. By convention
(this is how dbt tests work) the test **passes when it returns zero rows** — no
violations means all is well.

**Your task:** write a test that returns any order whose `total_amount` is negative.
An order total should never be below zero.

```
SELECT *
FROM orders
WHERE total_amount < 0;
```

The grader runs your test twice: against **clean** data (it must return nothing) and
against data with a bad row injected (it must catch it). A test that can't tell the
two apart isn't a test.

> Needs the stack: `./platform.sh up` first.
