-- This only loads the web feed. The store orders are missing entirely.
-- TODO: UNION ALL the store feed too, mapping its `total` column onto `amount`
-- and stamping source = 'store'.

INSERT INTO raw.orders_all (order_id, amount, source)
SELECT order_id, amount, 'web'
FROM landing.web_orders;
