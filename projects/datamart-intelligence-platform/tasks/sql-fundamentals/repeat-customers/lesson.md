### Filter groups with HAVING

`WHERE` filters individual rows *before* grouping. `HAVING` filters **groups**
*after* `GROUP BY` — it's how you ask questions like "which groups have more than N
rows?"

**Your task:** show `customer_id` and their order count, but only for customers who
placed **more than one** order.

```
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

Rule of thumb: if your condition uses an aggregate (`COUNT`, `SUM`, `AVG`), it belongs
in `HAVING`, not `WHERE`.
