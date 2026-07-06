INSERT INTO raw.products (sku, name, price)
SELECT DISTINCT ON (sku) sku, name, price
FROM landing.products_raw
ORDER BY sku, loaded_at DESC;
