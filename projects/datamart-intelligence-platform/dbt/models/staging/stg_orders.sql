{{
  config(
    materialized='view',
    schema='staging',
    tags=['staging', 'daily']
  )
}}

SELECT
  order_id,
  customer_id,
  order_date,
  total_amount,
  status
FROM {{ source('raw', 'orders') }}
WHERE order_date IS NOT NULL