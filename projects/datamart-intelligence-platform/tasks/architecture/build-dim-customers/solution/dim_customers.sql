INSERT INTO analytics.dim_customers (customer_id, customer_name, email)
SELECT customer_id, customer_name, email
FROM raw.customers;
