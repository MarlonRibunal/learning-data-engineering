# KPI cards

The tiles at the top of every dashboard — total revenue, order count, average order value. Each is a single number rolled up from all the rows.

## Your task

Write `kpi_cards(rows)` where `rows` is a list of order dicts (`order_id, day, category, amount`). Return a dict with exactly:

```python
{
    "total_revenue": <sum of amount>,
    "order_count":   <number of rows>,
    "avg_order_value": <total_revenue / order_count, rounded to 2 decimals>,
}
```

```python
def kpi_cards(rows):
    total = sum(r["amount"] for r in rows)
    count = len(rows)
    return {
        "total_revenue": total,
        "order_count": count,
        "avg_order_value": round(total / count, 2) if count else 0,
    }
```
