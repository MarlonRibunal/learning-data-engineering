### The headline KPIs

Every dashboard opens with a few big numbers — the KPIs a stakeholder checks first.
Serving is where you compute them precisely.

**Your task:** return **one row** with three metrics across all orders:
`total_orders`, `total_revenue` (sum), and `avg_order_value` (average, rounded to 2).

```
SELECT COUNT(*) AS total_orders,
       SUM(total_amount) AS total_revenue,
       ROUND(AVG(total_amount), 2) AS avg_order_value
FROM orders;
```

Graded on the exact numbers — hit **▶ Run query** to see your KPIs first.

> Needs the stack: `./platform.sh up` first.
