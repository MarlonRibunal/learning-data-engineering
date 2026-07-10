-- Source + target for the CDC (change-data-capture) task.
--
-- landing.customer_changes is a change feed: each row is an operation to apply
-- (I=insert, U=update, D=delete). raw.customers_cdc is the target, pre-loaded
-- with two customers. The learner applies inserts/updates as an upsert and
-- marks deletes with is_deleted (a soft delete). Rebuilt every reseed.

CREATE SCHEMA IF NOT EXISTS landing;
CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS landing.customer_changes;
CREATE TABLE landing.customer_changes (
    op          CHAR(1),   -- 'I' insert, 'U' update, 'D' delete
    customer_id INT,
    name        TEXT
);
INSERT INTO landing.customer_changes (op, customer_id, name) VALUES
    ('U', 10, 'Ana Smith'),  -- customer 10 changed her name
    ('I', 12, 'Cy'),         -- new customer
    ('D', 11, NULL);         -- customer 11 was deleted upstream

DROP TABLE IF EXISTS raw.customers_cdc;
CREATE TABLE raw.customers_cdc (
    customer_id INT PRIMARY KEY,
    name        TEXT,
    is_deleted  BOOLEAN DEFAULT false
);
INSERT INTO raw.customers_cdc (customer_id, name, is_deleted) VALUES
    (10, 'Ana', false),
    (11, 'Ben', false);
