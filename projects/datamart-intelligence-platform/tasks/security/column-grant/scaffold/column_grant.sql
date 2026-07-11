-- This grants SELECT on the WHOLE table, so the analyst can read ssn too.
-- TODO: grant column-level SELECT on only (customer_id, customer_name, email).
CREATE ROLE analyst;
GRANT USAGE ON SCHEMA analytics TO analyst;
GRANT SELECT ON analytics.customer_pii TO analyst;
