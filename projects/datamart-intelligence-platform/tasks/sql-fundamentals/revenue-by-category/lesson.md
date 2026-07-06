### Revenue by product category

Every analytics stack starts with a question like *"which categories make us the
most money?"* You answer it by **aggregating** rows up to one row per group.

**Your task:** write a query against the `orders` table that returns one row per
`category` with the total revenue for that category, ordered highest first.

Expected shape:

```
category    | revenue
------------+--------
Electronics | 750.00
Books       | 120.50
...
```

**Hints**
- `SUM(total_amount)` totals the revenue.
- `GROUP BY category` collapses rows to one per category.
- `ORDER BY ... DESC` puts the biggest first.

Hit **▶ Run query** to see your rows, then **Check my work**.
