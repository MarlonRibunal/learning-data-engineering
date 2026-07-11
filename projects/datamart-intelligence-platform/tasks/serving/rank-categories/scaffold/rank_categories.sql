-- TODO: add a real RANK() OVER (ORDER BY SUM(total_amount) DESC). Right now
-- every category is hard-coded to rank 1, which is wrong.
SELECT category,
       SUM(total_amount) AS revenue,
       1 AS rank
FROM orders
GROUP BY category;
