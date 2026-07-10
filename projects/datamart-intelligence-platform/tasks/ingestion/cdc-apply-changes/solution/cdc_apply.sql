INSERT INTO raw.customers_cdc (customer_id, name, is_deleted)
SELECT customer_id, name, false
FROM landing.customer_changes
WHERE op IN ('I', 'U')
ON CONFLICT (customer_id) DO UPDATE
    SET name = EXCLUDED.name, is_deleted = false;

UPDATE raw.customers_cdc
SET is_deleted = true
WHERE customer_id IN (
    SELECT customer_id FROM landing.customer_changes WHERE op = 'D'
);
