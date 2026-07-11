SELECT order_id
FROM raw.orders
WHERE order_date < DATE '2020-01-01'
   OR order_date > DATE '2030-01-01';
