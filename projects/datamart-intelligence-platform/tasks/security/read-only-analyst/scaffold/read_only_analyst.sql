-- Task: a read-only analyst role
--
-- Create a role `analyst` that can SELECT from analytics.customer_pii but cannot
-- modify it. This stub creates the role but grants it nothing, so it can't read yet.
--
-- TODO: grant USAGE on the schema and SELECT on the table (and nothing more).
CREATE ROLE analyst;
