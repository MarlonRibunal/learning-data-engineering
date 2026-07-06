### Revenue over time

Trends live in time series. A revenue line chart needs one row per day, in order.

**Your task:** return `order_date` and the total `revenue` for that day, ordered from
earliest to latest.

```
SELECT order_date, SUM(total_amount) AS revenue
FROM orders
GROUP BY order_date
ORDER BY order_date;
```

The grader checks the rows **and their order** — a time series in the wrong order is
a broken chart.

> Needs the stack: `./platform.sh up` first.
