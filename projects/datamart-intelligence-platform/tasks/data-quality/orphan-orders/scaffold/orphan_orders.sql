-- A data test returns the rows that VIOLATE the rule; it passes when it returns
-- nothing on good data. This stub returns nothing on ANY data, so it never catches
-- the problem.
--
-- TODO: replace the WHERE clause so this returns the offending rows.
SELECT *
FROM orders
WHERE false;
