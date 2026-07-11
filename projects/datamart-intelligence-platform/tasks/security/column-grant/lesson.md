# Column-level grants

**The scenario.** The analytics team needs the customer table — names, emails —
to do their job. But the same table has an `ssn` column, and nobody outside
compliance should ever see that. Granting `SELECT` on the *whole table* is too
blunt. Postgres lets you grant `SELECT` on **specific columns**, so you expose
exactly what's needed and nothing more. This is least privilege at the column
level.

## Table grant vs. column grant

```sql
-- too much: exposes EVERY column, ssn included
GRANT SELECT ON analytics.customer_pii TO analyst;

-- just right: only these columns
GRANT SELECT (customer_id, customer_name, email) ON analytics.customer_pii TO analyst;
```

With a column grant, `SELECT customer_name FROM customer_pii` works for the
analyst, but `SELECT ssn FROM customer_pii` is denied.

You check column privileges with `has_column_privilege(role, table, column,
'SELECT')` — the grader uses it to confirm `email` is readable and `ssn` is not.

## Your task

In `column_grant.sql`: create the `analyst` role, grant it `USAGE` on the
`analytics` schema, and grant **column-level** `SELECT` on
`customer_id, customer_name, email` (but **not** `ssn`) of
`analytics.customer_pii`:

```sql
CREATE ROLE analyst;
GRANT USAGE ON SCHEMA analytics TO analyst;
GRANT SELECT (customer_id, customer_name, email) ON analytics.customer_pii TO analyst;
```
