### Aggregate with AVG and round the result

Warehouses are where you compute the metrics a business actually looks at. Here you'll
build the **average order value** per status — and round it, because nobody wants to
read `290.16666667` on a dashboard.

**Your task:** complete `avg_order_value` so it returns one row per `status` with the
average `total_amount`, rounded to 2 decimal places.

```
SELECT status, ROUND(AVG(total_amount), 2) AS avg_amount
FROM {{ source('raw', 'orders') }}
GROUP BY status
```

`ROUND(value, 2)` keeps two decimals — small touch, real-world habit.

> Needs the stack: `./platform.sh up` first.
