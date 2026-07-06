### Join two sources in dbt

Marts often stitch together more than one source. Here you'll join the raw orders to
the raw customers to attribute revenue to a customer name.

**Your task:** complete `revenue_by_customer` so it returns each `customer_name` and
their total `revenue`.

```
SELECT c.customer_name, SUM(o.total_amount) AS revenue
FROM {{ source('raw', 'orders') }} o
JOIN {{ source('raw', 'customers') }} c ON o.customer_id = c.customer_id
GROUP BY c.customer_name
```

Same JOIN you learned in SQL Fundamentals — now producing a tested warehouse table.

> Needs the stack: `./platform.sh up` first.
