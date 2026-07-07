### Least privilege: a read-only role

The principle of **least privilege** says every user gets exactly the access they
need — and no more. An analyst who only reads data should not be able to change it.

**Your task:** create a role `analyst` that can `SELECT` from `analytics.customer_pii`
but cannot `INSERT`/`UPDATE`/`DELETE`.

```
CREATE ROLE analyst;
GRANT USAGE ON SCHEMA analytics TO analyst;
GRANT SELECT ON analytics.customer_pii TO analyst;
```

The grader checks the role can read (`SELECT` privilege) and confirms it *cannot*
write. Granting `ALL` would fail — least privilege means grant only what's needed.

> Needs the stack: `./platform.sh up` first.
