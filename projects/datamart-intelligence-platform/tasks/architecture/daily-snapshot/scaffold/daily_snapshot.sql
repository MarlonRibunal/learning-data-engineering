-- This only snapshots the shipped orders, so the as-of picture is incomplete.
-- TODO: snapshot ALL orders (drop the WHERE), each stamped 2026-03-01.
INSERT INTO analytics.orders_snapshot (snapshot_date, order_id, status, total_amount)
SELECT DATE '2026-03-01', order_id, status, total_amount
FROM raw.orders
WHERE status = 'shipped';
