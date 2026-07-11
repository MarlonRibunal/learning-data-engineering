SELECT order_id
FROM raw.orders
WHERE customer_id IS NULL;
