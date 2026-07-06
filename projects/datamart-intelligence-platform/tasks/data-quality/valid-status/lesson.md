### Write a data test: only valid statuses

Categorical columns should only hold known values. If a rogue `status` slips in,
every report that groups by status is quietly wrong.

**Your task:** write a test that returns any order whose `status` is **not** one of
`'shipped'`, `'pending'`, `'cancelled'`.

```
SELECT *
FROM orders
WHERE status NOT IN ('shipped', 'pending', 'cancelled');
```

Passes on clean data (returns nothing), catches the injected bad status.

> Needs the stack: `./platform.sh up` first.
