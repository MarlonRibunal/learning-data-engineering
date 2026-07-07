-- Task: build a fact table at the right grain
--
-- A fact table records events at a precise GRAIN — here, one row per order. Fill
-- analytics.fct_orders(order_id, customer_id, order_date, amount) from raw.orders,
-- keeping the foreign key to the customer dimension and the amount measure.
--
-- TODO: write the INSERT.
SELECT 1;
