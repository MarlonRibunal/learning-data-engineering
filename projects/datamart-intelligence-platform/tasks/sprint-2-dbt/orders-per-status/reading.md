## What dbt actually is

dbt (data build tool) owns the **T** in **ELT**. The old way was ETL: transform
data *before* loading it, in bespoke scripts. Cloud warehouses flipped that —
storage and compute are cheap, so you **E**xtract and **L**oad raw data first,
then **T**ransform it *inside* the warehouse with SQL. dbt is the tool that makes
that transformation layer maintainable.

The key idea: **a dbt model is just a `SELECT` statement in a `.sql` file.** dbt
takes that `SELECT`, wraps it in `CREATE TABLE AS` (or `CREATE VIEW`), and runs it
against your warehouse. You never write the DDL, the drops, or the load — you
describe *what the table should contain*, and dbt materializes it.

That one move brings software-engineering discipline to analytics SQL:

- **Version control** — models are files in git, reviewed in PRs.
- **Testing** — every model can have data tests that run on each build.
- **Documentation & lineage** — dbt knows how models depend on each other.
- **Environments** — the same code runs against dev and prod.

So when you "write a model," you're really declaring a managed, tested, versioned
table whose definition lives in code — the backbone of the modern data stack.

*Go deeper: dbt docs "About dbt"; the ETL→ELT shift.*
