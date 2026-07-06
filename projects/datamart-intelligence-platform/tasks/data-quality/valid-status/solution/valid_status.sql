SELECT *
FROM orders
WHERE status NOT IN ('shipped', 'pending', 'cancelled');
