SELECT order_id,
       CASE WHEN total_amount >= 100 THEN 'large' ELSE 'small' END AS order_size
FROM orders;
