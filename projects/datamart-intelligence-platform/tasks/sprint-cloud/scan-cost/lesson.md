# What a query costs

**The scenario.** On a serverless cloud warehouse like **BigQuery**, you don't
rent servers — you pay per query, and the price is set by **bytes scanned**
(BigQuery's on-demand rate is about **$5 per terabyte** read). That billing model
quietly rewrites how you write SQL: a careless `SELECT *` over a huge table can
cost real money, while scanning only the columns and partitions you need costs
cents.

## The math

Cost = terabytes scanned × price per TB. A terabyte is `1e12` bytes:

```python
def scan_cost(bytes_scanned, price_per_tb):
    terabytes = bytes_scanned / 1e12
    return round(terabytes * price_per_tb, 2)
```

`scan_cost(2_000_000_000_000, 5.0)` → `10.0` — scanning 2 TB at $5/TB is $10.
Now imagine that query runs hourly on a dashboard.

## Your task

Write `scan_cost(bytes_scanned, price_per_tb)` returning the dollar cost (bytes /
1e12 × price), rounded to 2 decimals. Internalizing this is *why* the next level
— partition pruning — matters.
