SELECT customer_id,
       SUM(total_amount) AS total_spend,
       RANK() OVER (ORDER BY SUM(total_amount) DESC) AS spend_rank
FROM orders
GROUP BY customer_id;
