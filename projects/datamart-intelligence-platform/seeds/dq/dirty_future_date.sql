-- Injects an order dated far in the future (a data-entry / clock bug).
INSERT INTO raw.orders (order_id, customer_id, order_date, total_amount, status, category, created_at)
VALUES (9998, 1, '2099-01-01', 99.00, 'shipped', 'Electronics', '2026-03-01 00:00:00');
