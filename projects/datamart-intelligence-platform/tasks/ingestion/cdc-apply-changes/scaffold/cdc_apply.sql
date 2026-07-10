-- This only handles brand-new inserts. It ignores updates and deletes, so
-- customer 10 keeps her old name and customer 11 never gets flagged.
-- TODO: upsert the 'I' AND 'U' rows (ON CONFLICT), then soft-delete the 'D' rows.

INSERT INTO raw.customers_cdc (customer_id, name)
SELECT customer_id, name
FROM landing.customer_changes
WHERE op = 'I';
