-- Injects a customer whose email duplicates an existing one (emails should be unique).
INSERT INTO raw.customers (customer_id, customer_name, email, created_at, updated_at)
VALUES (5, 'Ada Impostor', 'ada@example.com', '2026-03-01 00:00:00', '2026-03-01 00:00:00');
