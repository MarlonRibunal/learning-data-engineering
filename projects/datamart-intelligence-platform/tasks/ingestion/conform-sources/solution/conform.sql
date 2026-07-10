INSERT INTO raw.orders_all (order_id, amount, source)
SELECT order_id, amount, 'web'
FROM landing.web_orders
UNION ALL
SELECT order_id, total, 'store'
FROM landing.store_orders;
