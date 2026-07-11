### Conditional logic with CASE

`CASE` is SQL's if/else. It produces a value per row based on conditions — great for
bucketing, labelling, and cleaning data.

**Your task:** show `order_id` and an `order_size` label that is `'large'` when
`total_amount >= 100`, otherwise `'small'`.

```
SELECT order_id,
       CASE WHEN total_amount >= 100 THEN 'large' ELSE 'small' END AS order_size
FROM orders;
```

A `CASE` always ends with `END`. You can chain several `WHEN ... THEN ...` branches.
