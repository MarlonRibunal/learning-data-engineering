-- Source data for the raw schema the dbt models read from.
--
-- The grader runs this before each real-infra check (reseed-before / assert-after):
-- it rebuilds raw.* so a check is deterministic regardless of run order or prior
-- state. DROP+CREATE (not just TRUNCATE) so the schema stays current when columns
-- are added. Data is referentially consistent so the shipped dbt tests
-- (unique / not_null / relationships) pass on a correct model.
--
-- Also usable as a Postgres init script if you want the tables to exist on boot.

CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS raw.orders CASCADE;
DROP TABLE IF EXISTS raw.customers CASCADE;

CREATE TABLE raw.customers (
    customer_id   INTEGER PRIMARY KEY,
    customer_name TEXT,
    email         TEXT,
    created_at    TIMESTAMP,
    updated_at    TIMESTAMP
);

CREATE TABLE raw.orders (
    order_id     INTEGER PRIMARY KEY,
    customer_id  INTEGER,
    order_date   DATE,
    total_amount NUMERIC(10, 2),
    status       TEXT,
    category     TEXT,
    created_at   TIMESTAMP
);

INSERT INTO raw.customers (customer_id, customer_name, email, created_at, updated_at) VALUES
    (1, 'Ada Lovelace',     'ada@example.com',   '2026-01-02 09:00:00', '2026-01-02 09:00:00'),
    (2, 'Alan Turing',      'alan@example.com',  '2026-01-03 10:00:00', '2026-01-03 10:00:00'),
    (3, 'Grace Hopper',     'grace@example.com', '2026-01-04 11:00:00', '2026-01-04 11:00:00'),
    (4, 'Katherine Johnson','kj@example.com',    '2026-01-05 12:00:00', '2026-01-05 12:00:00');

INSERT INTO raw.orders (order_id, customer_id, order_date, total_amount, status, category, created_at) VALUES
    (1001, 1, '2026-02-01', 250.00, 'shipped',   'Electronics', '2026-02-01 08:00:00'),
    (1002, 1, '2026-02-03', 120.50, 'shipped',   'Books',       '2026-02-03 08:00:00'),
    (1003, 2, '2026-02-04',  75.00, 'pending',   'Clothing',    '2026-02-04 08:00:00'),
    (1004, 3, '2026-02-05', 500.00, 'shipped',   'Electronics', '2026-02-05 08:00:00'),
    (1005, 4, '2026-02-06',  40.25, 'cancelled', 'Sports',      '2026-02-06 08:00:00');
