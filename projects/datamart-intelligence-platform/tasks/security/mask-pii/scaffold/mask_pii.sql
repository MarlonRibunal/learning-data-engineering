-- Task: a PII-safe view
--
-- analytics.customer_pii holds sensitive columns (email, ssn). Build a view
-- analytics.customers_safe that dashboards can use WITHOUT exposing PII.
-- This stub exposes everything with SELECT * — fix it to select only safe columns.
--
-- TODO: select only the non-sensitive columns.
CREATE VIEW analytics.customers_safe AS
SELECT * FROM analytics.customer_pii;
