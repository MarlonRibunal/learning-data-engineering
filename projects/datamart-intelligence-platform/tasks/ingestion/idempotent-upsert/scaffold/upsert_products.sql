-- Task: make the load idempotent
--
-- This INSERT works the FIRST time, but the grader runs your load TWICE (like a
-- pipeline that re-runs). The second run fails with a duplicate-key error.
--
-- TODO: make it idempotent so re-running is safe. Hint: INSERT ... ON CONFLICT.
INSERT INTO raw.products (sku, name, price)
SELECT DISTINCT ON (sku) sku, name, price
FROM landing.products_raw
ORDER BY sku, loaded_at DESC;
