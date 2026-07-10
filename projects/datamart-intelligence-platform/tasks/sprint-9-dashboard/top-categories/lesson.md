# Top categories

A "top N" bar chart is a rollup, sorted **descending** by the metric, then cut to the first `n`. Ranking is where dashboards go wrong — forget the sort or the limit and the chart lies.

## Your task

Write `top_categories(rows, n)` returning a list of `{"category": ..., "revenue": ...}` — revenue summed per category, sorted **highest first**, keeping only the top `n`:

```python
def top_categories(rows, n):
    totals = {}
    for r in rows:
        totals[r["category"]] = totals.get(r["category"], 0) + r["amount"]
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    return [{"category": c, "revenue": v} for c, v in ranked[:n]]
```
