SELECT c.customer_name, SUM(o.total_amount) AS revenue
FROM {{ source('raw', 'orders') }} o
JOIN {{ source('raw', 'customers') }} c ON o.customer_id = c.customer_id
GROUP BY c.customer_name
