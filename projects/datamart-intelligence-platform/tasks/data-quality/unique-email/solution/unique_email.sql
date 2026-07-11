SELECT email
FROM raw.customers
GROUP BY email
HAVING COUNT(*) > 1;
