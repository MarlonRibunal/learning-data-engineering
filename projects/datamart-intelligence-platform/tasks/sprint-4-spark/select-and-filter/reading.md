## Lazy evaluation: the trick that lets Spark scale

Write `.filter(...).select(...)` in Spark and **nothing happens.** Spark doesn't
run each step as you write it — it records them as a plan and does nothing until
an **action** (`.collect()`, `.count()`, `.write`) demands a result. That
laziness is the whole reason Spark scales.

- **Transformations** (`select`, `filter`, `groupBy`, `join`) are lazy — they
  build up a recipe (a logical plan / DAG).
- **Actions** trigger execution of the whole recipe at once.

Why it matters: because Spark sees the *entire* chain before running anything, its
**Catalyst optimizer** can rewrite it — reorder filters, prune columns, push
predicates down to the data source so less is ever read. Run steps eagerly and
you'd forfeit all of that.

It's the same declarative spirit as SQL: you describe *what* you want across a
cluster of machines, and an optimizer decides *how*. The mental shift from "this
line runs now" to "I'm building a plan that runs on an action" is the first thing
that makes Spark click.

*Go deeper: transformations vs. actions; the Catalyst optimizer; lazy DAGs.*
