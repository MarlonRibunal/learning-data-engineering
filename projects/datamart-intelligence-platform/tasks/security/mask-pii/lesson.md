### Protect PII with a safe view

Not everyone who needs customer data needs the *sensitive* parts of it. A common
control is a **view** that exposes only the safe columns — dashboards and analysts
read the view, never the raw PII table.

**Your task:** build `analytics.customers_safe` exposing `customer_id` and
`customer_name`, but **not** `email` or `ssn`.

```
CREATE VIEW analytics.customers_safe AS
SELECT customer_id, customer_name
FROM analytics.customer_pii;
```

The scaffold's `SELECT *` leaks everything. The grader checks the view exposes
`customer_name` and does **not** expose `email` or `ssn`.

> Needs the stack: `./platform.sh up` first.
