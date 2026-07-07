### Build a dimension

A **dimension** describes the *things* in your business — customers, products,
dates. It has one clean row per business key and the attributes you'll slice reports
by. Dimensions are shared: many facts point at the same dimension.

**Your task:** fill `analytics.dim_customers(customer_id, customer_name, email)` with
one row per customer from `raw.customers`.

```
INSERT INTO analytics.dim_customers (customer_id, customer_name, email)
SELECT customer_id, customer_name, email
FROM raw.customers;
```

The grader checks there's exactly one row per customer — the defining property of a
dimension.

> Needs the stack: `./platform.sh up` first.
