INSERT INTO analytics.dim_customer_scd (customer_id, customer_name, valid_from, valid_to, is_current)
SELECT customer_id, customer_name, valid_from,
       LEAD(valid_from) OVER (PARTITION BY customer_id ORDER BY valid_from) AS valid_to,
       LEAD(valid_from) OVER (PARTITION BY customer_id ORDER BY valid_from) IS NULL AS is_current
FROM raw.customer_versions;
