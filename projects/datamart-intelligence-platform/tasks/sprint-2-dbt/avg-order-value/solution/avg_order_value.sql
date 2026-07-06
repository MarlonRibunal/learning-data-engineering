SELECT
    status,
    ROUND(AVG(total_amount), 2) AS avg_amount
FROM {{ source('raw', 'orders') }}
GROUP BY status
