## Slowly Changing Dimensions

Dimensions change — a customer moves, renames, switches segment. How you *handle*
that change is a modeling decision with a formal taxonomy: **Slowly Changing
Dimensions (SCD)**.

- **Type 1 — overwrite.** Replace the old value. Simple, but you **lose history**:
  last year's orders retroactively show this year's attributes. Fine when history
  doesn't matter (fixing a typo).
- **Type 2 — add a new row.** Keep every version as its own row, stamped with a
  validity window (`valid_from`/`valid_to`) and an `is_current` flag. History is
  preserved: a fact joins to the dimension version that was *current when the
  event happened*. This is the workhorse, and what you built.
- **Type 3 — add a column.** Keep only "previous" and "current" values side by
  side. Rare; for when you need limited history without new rows.

Type 2 is what makes a warehouse able to answer **"as of" questions** — "what
segment was this customer in *when they bought*?" — instead of only "what is
true now." That temporal correctness is the difference between a report you can
audit and one you can't.

*Go deeper: Kimball SCD types 0–6; "as-of" joins; effective-dating.*
