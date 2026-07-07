-- Seed for the security undercurrent.
--
-- Provides analytics.customer_pii (a table with sensitive columns) and cleans up
-- the `analyst` role + any customers_safe view so the security tasks grade
-- deterministically on every reseed.

CREATE SCHEMA IF NOT EXISTS analytics;

DROP VIEW IF EXISTS analytics.customers_safe;
DROP TABLE IF EXISTS analytics.customer_pii CASCADE;

-- Drop the role (and any privileges it holds) if a previous run created it.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analyst') THEN
        EXECUTE 'DROP OWNED BY analyst';
        EXECUTE 'DROP ROLE analyst';
    END IF;
END $$;

CREATE TABLE analytics.customer_pii (
    customer_id   INTEGER PRIMARY KEY,
    customer_name TEXT,
    email         TEXT,   -- sensitive
    ssn           TEXT    -- sensitive
);

INSERT INTO analytics.customer_pii (customer_id, customer_name, email, ssn) VALUES
    (1, 'Ada Lovelace',     'ada@example.com',   '111-11-1111'),
    (2, 'Alan Turing',      'alan@example.com',  '222-22-2222'),
    (3, 'Grace Hopper',     'grace@example.com', '333-33-3333'),
    (4, 'Katherine Johnson','kj@example.com',    '444-44-4444');
