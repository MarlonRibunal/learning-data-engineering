SELECT
    order_date,
    SUM(total_amount) AS revenue
FROM orders
GROUP BY order_date
ORDER BY order_date;
