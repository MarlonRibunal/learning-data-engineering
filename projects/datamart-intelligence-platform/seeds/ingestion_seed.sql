-- Source + target for the ingestion sprint.
--
-- `landing.products_raw` is a messy raw product feed: it has a duplicate SKU
-- (SKU1 appears twice, an older and a newer version). The learner ingests it into
-- a clean `raw.products` (one row per SKU). Rebuilt on every reseed so grading is
-- deterministic.

CREATE SCHEMA IF NOT EXISTS landing;
CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS landing.products_raw;
CREATE TABLE landing.products_raw (
    sku       TEXT,
    name      TEXT,
    price     NUMERIC(10, 2),
    loaded_at TIMESTAMP
);

INSERT INTO landing.products_raw (sku, name, price, loaded_at) VALUES
    ('SKU1', 'Widget',      9.99, '2026-03-01 00:00:00'),
    ('SKU2', 'Gadget',     19.99, '2026-03-01 00:00:00'),
    ('SKU3', 'Gizmo',       4.99, '2026-03-01 00:00:00'),
    ('SKU1', 'Widget Pro', 11.99, '2026-03-02 00:00:00');  -- newer version of SKU1

-- Clean target the learner loads into (starts empty each run).
DROP TABLE IF EXISTS raw.products;
CREATE TABLE raw.products (
    sku   TEXT PRIMARY KEY,
    name  TEXT,
    price NUMERIC(10, 2)
);
