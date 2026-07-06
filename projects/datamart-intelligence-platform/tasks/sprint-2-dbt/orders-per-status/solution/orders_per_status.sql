SELECT
    status,
    COUNT(*) AS order_count
FROM {{ source('raw', 'orders') }}
GROUP BY status
