-- Reference solution (kept out of the learner's workspace).
-- The grader never reads this file to decide pass/fail; it is here so a
-- contributor can see the intended answer and so `check` can be regression-tested.
SELECT
    category,
    SUM(amount) AS revenue
FROM orders
GROUP BY category
ORDER BY revenue DESC;
