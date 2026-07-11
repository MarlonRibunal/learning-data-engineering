-- TODO: return only the orders whose customer_id IS NULL. Right now this
-- returns every order, so it false-alarms on good data.
SELECT order_id
FROM raw.orders;
