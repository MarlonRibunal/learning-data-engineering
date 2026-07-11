## Reconciliation: proving a migration is safe

The final, non-negotiable step of any migration: **reconcile** before and after, and
prove nothing was silently lost or duplicated. A migration that drops 2% of rows is
*worse* than one that crashes — the crash you'd notice; the quiet 2% you'd ship, and
someone would trust.

What reconciliation checks, from cheap to thorough:

- **Row counts** — `count(before)` vs. `count(after)`. The fastest smoke test; a
  mismatch means stop and investigate. (You returned the *delta* per table, which
  doubles as a work-list of exactly what diverged.)
- **Control totals** — sum a key measure (total revenue) on both sides. Catches
  losses that preserve row count but corrupt values.
- **Row-level diff / checksums** — hash rows and compare sets to find *which* rows
  differ, not just that some do.

This is the same "trust, but verify" discipline as incident recovery, and the same
before/after logic as data-quality testing — applied to migrations. It's why safe
migrations run **old and new in parallel** for a while (dual-write, compare outputs)
before cutting over: reconciliation gives you the evidence to flip the switch, and
the confidence to *keep* it flipped.

An unreconciled migration is a hope; a reconciled one is a fact.

*Go deeper: reconciliation (row counts / control totals / checksums); dual-write &
parallel-run migrations.*
