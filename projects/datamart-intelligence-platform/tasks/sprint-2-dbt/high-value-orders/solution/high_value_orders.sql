SELECT order_id, total_amount
FROM {{ source('raw', 'orders') }}
WHERE total_amount > 100
