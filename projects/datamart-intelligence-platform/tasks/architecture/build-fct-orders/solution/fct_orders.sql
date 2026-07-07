INSERT INTO analytics.fct_orders (order_id, customer_id, order_date, amount)
SELECT order_id, customer_id, order_date, total_amount
FROM raw.orders;
