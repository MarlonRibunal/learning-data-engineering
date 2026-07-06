-- Injects an order for a customer_id that does not exist in raw.customers.
INSERT INTO raw.orders (order_id, customer_id, order_date, total_amount, status, category, created_at)
VALUES (9999, 999, '2026-03-01', 10.00, 'shipped', 'Electronics', '2026-03-01 00:00:00');
