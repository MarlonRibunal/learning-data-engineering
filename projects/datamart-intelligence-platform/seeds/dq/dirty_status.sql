-- Injects an order with a status outside the allowed set.
INSERT INTO raw.orders (order_id, customer_id, order_date, total_amount, status, category, created_at)
VALUES (9999, 1, '2026-03-01', 10.00, 'teleported', 'Electronics', '2026-03-01 00:00:00');
