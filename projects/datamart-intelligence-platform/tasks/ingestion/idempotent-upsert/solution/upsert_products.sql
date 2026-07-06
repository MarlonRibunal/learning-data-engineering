INSERT INTO raw.products (sku, name, price)
SELECT DISTINCT ON (sku) sku, name, price
FROM landing.products_raw
ORDER BY sku, loaded_at DESC
ON CONFLICT (sku) DO UPDATE
    SET name = EXCLUDED.name,
        price = EXCLUDED.price;
