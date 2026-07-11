-- Architecture: snapshot task. Current orders + an empty snapshot table.
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

DROP TABLE IF EXISTS raw.orders CASCADE;
CREATE TABLE raw.orders (
    order_id     INTEGER PRIMARY KEY,
    customer_id  INTEGER,
    order_date   DATE,
    total_amount NUMERIC(10, 2),
    status       TEXT,
    category     TEXT,
    created_at   TIMESTAMP
);
INSERT INTO raw.orders (order_id, customer_id, order_date, total_amount, status, category, created_at) VALUES
    (1001, 1, '2026-02-01', 250.00, 'shipped',   'Electronics', '2026-02-01 08:00'),
    (1002, 1, '2026-02-03', 120.50, 'shipped',   'Books',       '2026-02-03 08:00'),
    (1003, 2, '2026-02-04',  75.00, 'pending',   'Clothing',    '2026-02-04 08:00'),
    (1004, 3, '2026-02-05', 500.00, 'shipped',   'Electronics', '2026-02-05 08:00'),
    (1005, 4, '2026-02-06',  40.25, 'cancelled', 'Sports',      '2026-02-06 08:00');

DROP TABLE IF EXISTS analytics.orders_snapshot CASCADE;
CREATE TABLE analytics.orders_snapshot (
    snapshot_date DATE,
    order_id      INTEGER,
    status        TEXT,
    total_amount  NUMERIC(10, 2)
);
