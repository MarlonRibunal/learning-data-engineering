{{
  config(
    materialized='view',
    schema='staging',
    tags=['staging', 'daily']
  )
}}

SELECT
  customer_id,
  customer_name,
  email,
  created_at,
  updated_at
FROM {{ source('raw', 'customers') }}
WHERE email IS NOT NULL