ALTER TABLE analytics.customer_pii ENABLE ROW LEVEL SECURITY;

CREATE POLICY analyst_select ON analytics.customer_pii
    FOR SELECT USING (true);
