-- This marks EVERY version as current and leaves valid_to empty, so history
-- has no valid ranges and each customer looks like it has multiple "current"
-- rows. TODO: use LEAD(valid_from) OVER (PARTITION BY customer_id ORDER BY
-- valid_from) to fill valid_to, and set is_current only when there's no next
-- version.
INSERT INTO analytics.dim_customer_scd (customer_id, customer_name, valid_from, valid_to, is_current)
SELECT customer_id, customer_name, valid_from, NULL, true
FROM raw.customer_versions;
