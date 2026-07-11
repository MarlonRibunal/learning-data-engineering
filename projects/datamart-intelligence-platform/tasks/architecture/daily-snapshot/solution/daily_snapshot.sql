INSERT INTO analytics.orders_snapshot (snapshot_date, order_id, status, total_amount)
SELECT DATE '2026-03-01', order_id, status, total_amount
FROM raw.orders;
