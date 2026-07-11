## Modularity and the analytics engineer

Joining two sources into a mart looks like plain SQL, but doing it *the dbt way*
is really about **modularity** — the principle that turned analytics from
copy-pasted queries into engineering.

Before dbt, the same join lived in a dozen dashboards, each slightly different,
each breaking independently. dbt's answer is **DRY** (don't repeat yourself):
model a join or a metric **once**, as a `ref`-able model, and everything
downstream reuses it. Change the definition in one file and every consumer
updates on the next build.

This is the job of the **analytics engineer** — a role dbt essentially created,
sitting between the data engineer (who moves and lands raw data) and the analyst
(who asks business questions). The analytics engineer owns the transformation
layer: clean, tested, documented, modular models that everyone trusts.

The tools that make it modular:

- **`ref()`** to compose models instead of re-querying raw tables.
- **CTEs** (`WITH ...`) to break one model into readable, named steps.
- **macros** (Jinja functions) to reuse SQL patterns across models.

So a "join in dbt" is a building block others stand on — which is why getting it
right, tested, and named well matters more than the SQL itself.

*Go deeper: "analytics engineering"; dbt macros and the DRY principle.*
