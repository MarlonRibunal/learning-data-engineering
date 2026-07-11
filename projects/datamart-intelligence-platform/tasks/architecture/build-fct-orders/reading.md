## Fact tables, grain, and additivity

If dimensions are the nouns, **fact tables** are the verbs — one row per business
*event* (an order, a click, a payment), holding the **measures** (amounts,
quantities) plus **foreign keys** to the dimensions that give them context. Facts
are usually long and narrow: billions of rows, few columns.

Three concepts define a good fact table:

- **Grain** — *exactly* what one row represents ("one row per order line").
  Declaring the grain first, before any column, is the single most important
  modeling decision; a fuzzy grain produces double-counting you can't debug later.
- **Additivity** — a measure is *additive* if summing it across any dimension is
  meaningful (revenue is). Some are *semi-additive* (an account balance sums over
  accounts but not over time) or *non-additive* (a ratio/percentage — never sum
  them, recompute from components). Knowing which prevents nonsense aggregates.
- **Referential integrity** — every foreign key must resolve to a real dimension
  row, or facts silently drop out of joins (the orphan problem, one lifecycle
  earlier).

Fact + dimension, joined on clean keys at a well-declared grain, is the shape most
analytical queries are fastest and simplest against.

*Go deeper: fact-table grain; additive/semi-/non-additive measures; Kimball.*
