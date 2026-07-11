## Completeness and the trouble with NULL

**Completeness** asks: are the values that *should* be there, there? A `not_null`
test on a required column (every order must have a customer) is the guard — and
it's one of dbt's four built-in tests for good reason: missing keys quietly
break everything downstream.

`NULL` deserves respect, because it doesn't behave like other values:

- **`NULL` is "unknown", not "empty".** It's not `0`, not `''` — it's the absence
  of a value, and comparisons return *unknown*, which is why you test with
  `IS NULL`, never `= NULL`.
- **`NULL`s vanish from joins and filters.** An order with a `NULL` customer_id
  won't match any customer in a join, so it silently disappears from per-customer
  reports — under-counting with no error.
- **`NULL`s distort aggregates.** `AVG` ignores them (changing the denominator);
  `COUNT(col)` skips them while `COUNT(*)` includes the row.

Completeness has a *severity* spectrum: a null in a display field is cosmetic; a
null in a **key or a join column** is a data-integrity emergency. Knowing which
columns are load-bearing — and testing those hardest — is the skill.

*Go deeper: SQL three-valued logic; `NULL` in joins/aggregates; dbt `not_null`.*
