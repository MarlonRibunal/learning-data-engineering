SELECT status,
       ROUND(AVG(total_amount), 2) AS avg_order_value
FROM orders
GROUP BY status;
