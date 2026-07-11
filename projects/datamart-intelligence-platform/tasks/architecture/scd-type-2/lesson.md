# Slowly changing dimension (type 2)

**The scenario.** A customer changes her name. If your dimension just
**overwrites** the old value (that's an SCD *type 1*), every historical report
retroactively changes too — last year's orders now show this year's name, and
your "who ordered what, when" story is corrupted. **SCD type 2** instead keeps
*every version as its own row*, stamped with the window of time it was valid and
a flag for the current one. It's the standard way warehouses preserve history.

## The shape

Each version row gets:

- **`valid_from`** — when this version started (given).
- **`valid_to`** — when the *next* version started (or `NULL` if it's current).
- **`is_current`** — `true` for the latest version of each customer.

The trick is that `valid_to` and `is_current` both depend on the *next* row —
which is exactly what the `LEAD()` window function gives you:

```sql
INSERT INTO analytics.dim_customer_scd (customer_id, customer_name, valid_from, valid_to, is_current)
SELECT customer_id, customer_name, valid_from,
       LEAD(valid_from) OVER (PARTITION BY customer_id ORDER BY valid_from) AS valid_to,
       LEAD(valid_from) OVER (PARTITION BY customer_id ORDER BY valid_from) IS NULL AS is_current
FROM raw.customer_versions;
```

`LEAD(valid_from)` looks ahead to the next version's start date within each
customer. When there is no next version, it's `NULL` — so `valid_to` is `NULL`
and `is_current` is `true`. That's the whole pattern.

## Your task

Build `analytics.dim_customer_scd` from `raw.customer_versions`: one row per
version, with `valid_from`, a `valid_to` (next version's start, `NULL` if
current), and an `is_current` flag.
