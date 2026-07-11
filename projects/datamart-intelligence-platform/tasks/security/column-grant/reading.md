## Defense in depth, column by column

A table-level `GRANT` is all-or-nothing; **column-level grants** let you expose
some columns of a table and withhold others (names yes, SSN no). This is
**fine-grained access control**, and it embodies a second security principle:
**defense in depth** — many small, overlapping controls rather than one big wall.

Why layers beat a single gate: if any one control fails (a misconfigured view, a
forgotten role, an over-broad grant), the others still contain the damage.
Column-level grants add a layer *inside* the table itself, so even a role that can
query it can't read the sensitive columns.

The broader landscape of "who sees which columns":

- **Column grants** (this task) — the database refuses `SELECT` on a column.
- **Data classification / tagging** — label columns as `pii`/`confidential`, then
  drive policy from the tags (modern warehouses like Snowflake do this).
- **Dynamic masking** — the *same* column returns real values to privileged roles
  and masked values to others, decided at query time.

Column-level control is where least-privilege gets precise: not just "can you read
this table," but "which *parts* of it."

*Go deeper: column-level security; data classification/tagging; dynamic masking.*
