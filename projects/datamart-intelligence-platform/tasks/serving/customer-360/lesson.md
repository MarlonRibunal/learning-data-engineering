### Build a "customer 360" serving table

Dashboards and downstream teams rarely query raw tables directly — they read a
**serving table**: a clean, purpose-built dataset. Here you build a classic one, a
per-customer summary ("customer 360").

**Your task:** fill the empty `analytics.customer_360(customer_name, order_count,
total_spend)` with one row per customer. Use a `LEFT JOIN` so a customer with no
orders still appears (with 0), and `COALESCE` to turn a NULL sum into 0.

```
INSERT INTO analytics.customer_360 (customer_name, order_count, total_spend)
SELECT c.customer_name,
       COUNT(o.order_id)                AS order_count,
       COALESCE(SUM(o.total_amount), 0) AS total_spend
FROM raw.customers c
LEFT JOIN raw.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name;
```

> Needs the stack: `./platform.sh up` first.
