-- TODO: return only orders whose order_date is before 2020 or after 2030.
-- Right now this returns every order, so it false-alarms on good data.
SELECT order_id
FROM raw.orders;
