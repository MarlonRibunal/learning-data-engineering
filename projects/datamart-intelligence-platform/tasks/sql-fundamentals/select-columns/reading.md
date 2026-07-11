## The idea behind SELECT

SQL is a **declarative** language: you describe *what* you want, not *how* to get
it. `SELECT order_id, status FROM orders` says "give me these two attributes of
every order" — the database's query planner decides how to actually fetch them.
That separation is SQL's superpower and why it has outlived every "SQL killer."

Choosing columns is called **projection** in relational algebra (the math under
SQL). It sounds trivial, but it matters more than beginners expect:

- **Columnar storage.** Modern analytics warehouses (BigQuery, Snowflake,
  Redshift, DuckDB) store each *column* together on disk, not each row. When you
  project only the columns you need, the engine reads only those columns' files
  and skips the rest — often a 10× speedup versus `SELECT *`. Naming columns
  isn't just tidy; on a warehouse it's a performance decision.
- **Contracts.** The columns you select are a contract with everything
  downstream. `SELECT *` couples you to the table's *current* shape; if someone
  adds or reorders columns, `*`-based code can silently break or shift.

So the humble `SELECT col1, col2` is really you stating an explicit, stable,
efficient contract over your data — the mindset the rest of SQL builds on.

*Go deeper: "SQL and Relational Theory" (C.J. Date); any intro to columnar
storage.*
