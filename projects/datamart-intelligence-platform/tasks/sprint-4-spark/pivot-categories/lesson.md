# Pivot categories into columns

**The scenario.** You have long data — one row per (customer, category) spend —
and you want it **wide**: one row per customer, a *column* per category, ready
to drop into a spreadsheet or a heatmap. That reshape is a **pivot**, and Spark
does it natively.

## Pivot + fill

```python
orders.groupBy("customer_id").pivot("category").sum("amount").fillna(0)
```

- **`groupBy("customer_id")`** — one row per customer.
- **`.pivot("category")`** — turn each distinct category value into its own
  column.
- **`.sum("amount")`** — the value that fills each cell.
- **`.fillna(0)`** — a customer with no orders in a category gets a `NULL`; fill
  those with `0` so the grid is clean and the math works downstream.

## Your task

Write `transform(orders)` returning one row per **`customer_id`** with a column
per **`category`** holding that customer's summed `amount` (missing combinations
filled with `0`).
