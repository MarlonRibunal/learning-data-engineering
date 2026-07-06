SELECT category, SUM(total_amount) AS revenue
FROM orders
GROUP BY category
ORDER BY revenue DESC;
