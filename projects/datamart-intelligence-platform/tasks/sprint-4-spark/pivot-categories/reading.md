## Long vs. wide, and the cost of pivoting

Reshaping long data (one row per customer-category) into wide (one row per
customer, a column per category) is a **pivot** — and it sits at the heart of a
recurring data-engineering choice.

- **Long / tall / tidy** — one measurement per row (`customer, category, amount`).
  Flexible, easy to aggregate and add new categories, the natural shape for fact
  tables and storage.
- **Wide** — one row per entity, categories spread across columns. Easier for
  humans, spreadsheets, and some ML features, but brittle: a *new* category means a
  *new column* (a schema change).

Pivoting is more expensive than it looks on a cluster. Spark must first learn the
**distinct values** of the pivot column (an extra pass, unless you supply them),
then build a column per value. High-cardinality pivots (pivoting on user_id, say)
explode into thousands of mostly-empty columns — usually a modeling mistake.

The rule of thumb: **store long, present wide.** Keep data tall and normalized
where it lives; pivot to wide only at the serving/reporting edge, for a known,
small set of categories.

*Go deeper: tidy/long vs. wide data; Spark `pivot` cost & explicit value lists.*
