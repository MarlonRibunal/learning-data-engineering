SELECT category,
       SUM(total_amount) AS revenue,
       RANK() OVER (ORDER BY SUM(total_amount) DESC) AS rank
FROM orders
GROUP BY category;
