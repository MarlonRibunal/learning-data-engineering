## Tests: the data contract

The feature that most separates dbt from "a folder of SQL" is **tests**. A dbt
test is an assertion about your data that runs every time you build — a query
that should return **zero** rows, where each returned row is a failure.

dbt ships four generic tests you attach in YAML, no SQL required:

- **`unique`** — no duplicate values in a column (e.g. a primary key).
- **`not_null`** — a required column is never empty.
- **`accepted_values`** — a column only holds an allowed set (e.g. status in
  shipped/pending/cancelled).
- **`relationships`** — every foreign key matches a row in the referenced table
  (referential integrity).

And you can write **singular tests** — any custom `SELECT` that returns the bad
rows (exactly the "data test" idea from the Data Quality sprint).

Why it matters: tests turn tribal knowledge ("orders should never be negative")
into an executable **contract** that fails the build the moment it's violated.
`dbt build` runs your models *and* their tests together, so broken data can't
silently reach a dashboard — the same discipline unit tests bring to app code.

*Go deeper: dbt "Tests" (generic vs singular); the idea of data contracts.*
