-- Two source feeds with different shapes, plus the conformed target.
--
-- landing.web_orders and landing.store_orders describe the same thing (an
-- order) but name the money column differently (amount vs total). The learner
-- unions them into one raw.orders_all, conforming the columns and stamping the
-- source. Rebuilt every reseed.

CREATE SCHEMA IF NOT EXISTS landing;
CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS landing.web_orders;
CREATE TABLE landing.web_orders (order_id INT, amount NUMERIC(10, 2));
INSERT INTO landing.web_orders VALUES (1, 100.00), (2, 20.00);

DROP TABLE IF EXISTS landing.store_orders;
CREATE TABLE landing.store_orders (order_id INT, total NUMERIC(10, 2));
INSERT INTO landing.store_orders VALUES (3, 30.00), (4, 60.00);

DROP TABLE IF EXISTS raw.orders_all;
CREATE TABLE raw.orders_all (
    order_id INT,
    amount   NUMERIC(10, 2),
    source   TEXT
);
