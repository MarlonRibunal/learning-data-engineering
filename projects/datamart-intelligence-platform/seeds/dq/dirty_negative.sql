-- Injects a negative-amount order (a value that should never exist).
INSERT INTO raw.orders (order_id, customer_id, order_date, total_amount, status, category, created_at)
VALUES (9999, 1, '2026-03-01', -50.00, 'shipped', 'Electronics', '2026-03-01 00:00:00');
