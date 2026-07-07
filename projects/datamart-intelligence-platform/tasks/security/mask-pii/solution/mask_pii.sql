CREATE VIEW analytics.customers_safe AS
SELECT customer_id, customer_name
FROM analytics.customer_pii;
