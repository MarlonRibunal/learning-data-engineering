-- Injects an order with no customer_id (every order must belong to a customer).
INSERT INTO raw.orders (order_id, customer_id, order_date, total_amount, status, category, created_at)
VALUES (9999, NULL, '2026-03-01', 42.00, 'shipped', 'Electronics', '2026-03-01 00:00:00');
