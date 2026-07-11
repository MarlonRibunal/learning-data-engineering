## Keys and uniqueness

Uniqueness sounds trivial until you ask *which* column should be unique — and that
question is really about **keys**.

- A **primary / surrogate key** (`customer_id`) is guaranteed unique by the
  database; testing it is belt-and-suspenders.
- A **natural / business key** (`email`) identifies a real-world entity but often
  has *no* database constraint — so duplicates creep in, and each one means the
  same person counted twice in every "how many customers" metric.

Uniqueness failures are especially insidious because they inflate quietly: a
`COUNT(DISTINCT customer_id)` looks fine while `email` silently double-counts the
same human who signed up twice. The `GROUP BY ... HAVING COUNT(*) > 1` test is the
universal detector.

This also connects to **grain** — the level of detail one row represents. A table
is "one row per customer" *only if* the customer key is truly unique; a duplicate
email breaks that promise and every aggregate that assumed it. Verifying the grain
(unique key) is the first thing to check on any table you're handed, which is why
`unique` is one of dbt's four built-in tests.

*Go deeper: natural vs. surrogate keys; table "grain"; dbt `unique`.*
