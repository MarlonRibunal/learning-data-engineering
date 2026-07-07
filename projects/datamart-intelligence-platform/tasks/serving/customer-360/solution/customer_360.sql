INSERT INTO analytics.customer_360 (customer_name, order_count, total_spend)
SELECT
    c.customer_name,
    COUNT(o.order_id)                   AS order_count,
    COALESCE(SUM(o.total_amount), 0)    AS total_spend
FROM raw.customers c
LEFT JOIN raw.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name;
