-- TODO: return a RUNNING (cumulative) revenue total by date, using
-- SUM(total_amount) OVER (ORDER BY order_date). Right now this just returns
-- each day's own amount, not the cumulative total.
SELECT order_date, total_amount AS cumulative_revenue
FROM orders
ORDER BY order_date;
