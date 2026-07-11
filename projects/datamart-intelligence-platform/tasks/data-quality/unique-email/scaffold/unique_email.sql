-- TODO: return only the emails that appear more than once. Right now this
-- returns EVERY email, so it false-alarms on perfectly good data.
SELECT email
FROM raw.customers;
