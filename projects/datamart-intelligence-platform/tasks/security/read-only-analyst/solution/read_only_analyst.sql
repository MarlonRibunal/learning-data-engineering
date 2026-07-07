CREATE ROLE analyst;
GRANT USAGE ON SCHEMA analytics TO analyst;
GRANT SELECT ON analytics.customer_pii TO analyst;
