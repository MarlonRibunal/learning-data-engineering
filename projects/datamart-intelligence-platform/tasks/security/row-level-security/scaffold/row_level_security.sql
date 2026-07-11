-- This enables RLS but never adds a policy — which locks EVERYONE out.
-- TODO: also CREATE POLICY ... FOR SELECT USING (true) on the table.
ALTER TABLE analytics.customer_pii ENABLE ROW LEVEL SECURITY;
