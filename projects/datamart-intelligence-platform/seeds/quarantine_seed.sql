-- Source + targets for the "quarantine bad rows" ingestion task.
--
-- landing.orders_raw is a messy order feed: some rows are invalid (a missing
-- customer_id, a negative amount). The learner loads good rows into
-- raw.orders_clean and routes bad rows to raw.orders_quarantine. Rebuilt every
-- reseed so grading is deterministic.

CREATE SCHEMA IF NOT EXISTS landing;
CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS landing.orders_raw;
CREATE TABLE landing.orders_raw (
    order_id    INT,
    customer_id INT,
    amount      NUMERIC(10, 2)
);
INSERT INTO landing.orders_raw (order_id, customer_id, amount) VALUES
    (1, 10, 100.00),   -- valid
    (2, NULL, 50.00),  -- invalid: no customer
    (3, 11, -20.00),   -- invalid: negative amount
    (4, 12, 30.00);    -- valid

DROP TABLE IF EXISTS raw.orders_clean;
CREATE TABLE raw.orders_clean (
    order_id    INT PRIMARY KEY,
    customer_id INT,
    amount      NUMERIC(10, 2)
);

DROP TABLE IF EXISTS raw.orders_quarantine;
CREATE TABLE raw.orders_quarantine (
    order_id    INT,
    customer_id INT,
    amount      NUMERIC(10, 2),
    reason      TEXT
);
