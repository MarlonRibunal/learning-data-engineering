## Row-level security and multi-tenancy

Column grants control *which columns* a role sees; **Row-Level Security (RLS)**
controls *which rows*. The database attaches a **policy** — a predicate silently
`AND`-ed into every query — so a role only ever sees rows it's allowed to, no
matter how the query is written.

Its killer application is **multi-tenancy**: one physical table holds every
customer's (or region's, or team's) data, and an RLS policy like
`USING (tenant_id = current_setting('app.tenant'))` guarantees tenant A can never
read tenant B's rows — enforced by the database, not by hoping every application
query remembered its `WHERE` clause. That "enforced below the app" property is the
whole point: application bugs can't leak across the boundary.

The gotcha you met in the task is worth re-stating: **enabling RLS without a
policy denies everyone** (except the owner). RLS defaults to deny; a policy is
what lets specific rows through. Forgetting the policy has taken down many a
dashboard.

RLS trades a little query overhead and complexity for a strong, centralized
guarantee — the row-level twin of least privilege.

*Go deeper: Postgres RLS policies; multi-tenant data isolation patterns.*
