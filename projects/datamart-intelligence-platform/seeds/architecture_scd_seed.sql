-- Architecture: SCD type-2 task. A version history + an empty SCD dimension.
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

DROP TABLE IF EXISTS raw.customer_versions CASCADE;
CREATE TABLE raw.customer_versions (
    customer_id   INTEGER,
    customer_name TEXT,
    valid_from    DATE
);
-- customer 1 changed her name; customer 2 has a single version
INSERT INTO raw.customer_versions (customer_id, customer_name, valid_from) VALUES
    (1, 'Ada',          '2026-01-01'),
    (1, 'Ada Lovelace', '2026-06-01'),
    (2, 'Alan',         '2026-01-01');

DROP TABLE IF EXISTS analytics.dim_customer_scd CASCADE;
CREATE TABLE analytics.dim_customer_scd (
    customer_id   INTEGER,
    customer_name TEXT,
    valid_from    DATE,
    valid_to      DATE,
    is_current    BOOLEAN
);
