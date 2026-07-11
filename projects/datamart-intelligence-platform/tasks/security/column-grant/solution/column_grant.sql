CREATE ROLE analyst;
GRANT USAGE ON SCHEMA analytics TO analyst;
GRANT SELECT (customer_id, customer_name, email) ON analytics.customer_pii TO analyst;
