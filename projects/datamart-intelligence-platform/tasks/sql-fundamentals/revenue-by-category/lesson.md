### Revenue by product category

Every analytics stack starts with a question like *"which categories make us the
most money?"* You answer it by **aggregating** rows up to one row per group.

**Your task:** write a query against the `orders` table that returns one row per
`category` with the total revenue for that category, ordered highest first.

The `orders` table has (at least): `order_id`, `category`, `amount`.

Expected shape:

```
category    | revenue
------------+--------
Electronics | 5000
Clothing    | 4000
...
```

**Hints**
- `SUM(amount)` totals the revenue.
- `GROUP BY category` collapses rows to one per category.
- `ORDER BY ... DESC` puts the biggest first.

Edit your file on the right, then hit **Check my work**.
