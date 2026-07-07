### Build a fact table (mind the grain)

A **fact table** records *events* — orders, clicks, payments — with numeric
**measures** (amount) and **foreign keys** to dimensions (which customer). The single
most important decision is the **grain**: what one row means. Here it's *one row per
order*. Get the grain wrong and every number built on it is wrong.

**Your task:** fill `analytics.fct_orders(order_id, customer_id, order_date, amount)`
from `raw.orders` — one row per order, `amount = total_amount`, keyed to the customer
dimension.

```
INSERT INTO analytics.fct_orders (order_id, customer_id, order_date, amount)
SELECT order_id, customer_id, order_date, total_amount
FROM raw.orders;
```

The grader checks the grain (one row per order, no duplicates) and referential
integrity (every fact keys to a real customer in `dim_customers`) — that's a star
schema.

> Needs the stack: `./platform.sh up` first.
