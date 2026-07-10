-- TODO: load only the valid rows into raw.orders_clean, and route the invalid
-- rows (missing customer_id, or negative amount) into raw.orders_quarantine
-- with a reason. Right now this loads EVERYTHING into clean, which is wrong.

INSERT INTO raw.orders_clean (order_id, customer_id, amount)
SELECT order_id, customer_id, amount
FROM landing.orders_raw;
