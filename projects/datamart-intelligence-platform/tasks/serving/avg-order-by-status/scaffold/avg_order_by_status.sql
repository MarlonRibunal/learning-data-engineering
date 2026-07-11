-- TODO: return the AVERAGE order value per status. Right now this returns the
-- SUM, which is a different (and wrong) number.
SELECT status,
       ROUND(SUM(total_amount), 2) AS avg_order_value
FROM orders
GROUP BY status;
