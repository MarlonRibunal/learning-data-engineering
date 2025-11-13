-- Custom test to ensure order amounts are positive
SELECT
  order_id,
  total_amount
FROM {{ ref('stg_orders') }}
WHERE total_amount < 0