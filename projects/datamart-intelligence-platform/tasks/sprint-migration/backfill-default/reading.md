## Backfilling a new column without clobbering

Adding a column and filling a default *only where it's missing* looks trivial, but
it encodes the cardinal rule of any migration: **never destroy data you can't
recover.** Overwriting rows that already had a real value — clobbering — is the
migration disaster that turns "add a column" into "lose a column's worth of truth."

The ideas:

- **Additive by default.** Safe schema changes *add* (a nullable column, a new
  table); they don't mutate or drop in place. Adding a column with a backfilled
  default is additive; blindly overwriting is not.
- **Preserve existing values.** `row.get(col, default)` — keep what's there, fill
  only the gap — is the difference between enriching data and corrupting it. The
  same "don't overwrite real data" instinct behind upserts and SCDs.
- **Defaults are a modeling choice.** What does "missing region" *mean*? `UNKNOWN`
  vs. `NULL` vs. inferred-from-another-column each say something different downstream
  — a default is a small but real semantic decision, not just a placeholder.
- **Migrations should be reversible / testable.** Ideally you can dry-run, verify,
  and roll back. Which is exactly why the *next* step reconciles counts.

Backfilling well is enrichment that leaves every real value untouched — expansion,
never destruction.

*Go deeper: additive vs. destructive migrations; backfill defaults; reversible
migrations.*
