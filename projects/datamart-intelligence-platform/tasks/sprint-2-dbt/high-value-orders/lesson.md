### Filter rows inside a dbt model

A dbt model is just a `SELECT` — so everything you learned in SQL Fundamentals works
here, now materialized as a managed, tested table.

**Your task:** complete `high_value_orders` so it returns `order_id` and `total_amount`
for only the orders worth **more than 100**.

```
SELECT order_id, total_amount
FROM {{ source('raw', 'orders') }}
WHERE total_amount > 100
```

`dbt build` materializes it and checks `order_id` is unique + not null; the grader also
confirms you kept the right number of rows.

> Needs the stack: `./platform.sh up` first.
