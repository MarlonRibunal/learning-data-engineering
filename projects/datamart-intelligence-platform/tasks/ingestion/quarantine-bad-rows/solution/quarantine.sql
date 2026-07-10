INSERT INTO raw.orders_clean (order_id, customer_id, amount)
SELECT order_id, customer_id, amount
FROM landing.orders_raw
WHERE customer_id IS NOT NULL AND amount >= 0;

INSERT INTO raw.orders_quarantine (order_id, customer_id, amount, reason)
SELECT order_id, customer_id, amount,
       CASE WHEN customer_id IS NULL THEN 'missing customer_id'
            WHEN amount < 0        THEN 'negative amount'
       END
FROM landing.orders_raw
WHERE customer_id IS NULL OR amount < 0;
