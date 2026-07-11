# Row-level security

**The scenario.** Column grants control *which columns* a role sees. Sometimes
you need to control *which rows* — a regional manager should see only their
region's customers, a tenant should see only their own data. Postgres
**Row-Level Security (RLS)** enforces that in the database itself, so no
application bug can leak rows across the boundary.

## Two parts, both required

RLS is off until you turn it on, and once on it **denies every row** until you
add a policy that lets some through:

```sql
-- 1. turn on row filtering for the table
ALTER TABLE analytics.customer_pii ENABLE ROW LEVEL SECURITY;

-- 2. define which rows are visible (USING is the visibility predicate)
CREATE POLICY analyst_select ON analytics.customer_pii
    FOR SELECT USING (true);
```

The gotcha to internalize: **enabling RLS without a policy locks everyone out**
(except the owner) — a real-world footgun that takes down dashboards. A policy's
`USING (...)` clause is the row filter; `true` means "all rows" here, but in
production it'd be something like `region = current_setting('app.region')`.

## Your task

In `row_level_security.sql`, **enable RLS** on `analytics.customer_pii` **and**
create a `SELECT` policy on it. The grader checks both — RLS on, and at least
one policy present.
