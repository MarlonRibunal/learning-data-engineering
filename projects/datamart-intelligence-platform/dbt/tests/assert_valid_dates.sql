-- Custom test to ensure no future dates
SELECT
  order_id,
  order_date
FROM {{ ref('stg_orders') }}
WHERE order_date > CURRENT_DATE