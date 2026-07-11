## Denormalization for serving

Upstream, you *normalized* — split data into tidy tables (customers, orders) with
no redundancy, so writes stay consistent. The serving layer often does the
opposite on purpose: **denormalize** — pre-join and flatten everything about a
customer into one wide row (a "customer 360").

Why deliberately duplicate? Because serving optimizes for **reads**, not writes:

- **Speed** — a dashboard reads one pre-joined table instead of joining five at
  query time. On columnar warehouses, a wide "**One Big Table**" (OBT) is often
  the fastest thing you can build.
- **Simplicity** — analysts and BI tools get every attribute in one place, no join
  logic to get wrong.

The cost is redundancy and rebuild: denormalized tables can drift and must be
recomputed when sources change (which is why they're *derived* marts, rebuilt by
dbt, not sources of truth).

This is the core trade-off of data modeling: **normalize for integrity upstream,
denormalize for performance at serving.** Knowing *when* to flip is a defining
data-engineering judgment call.

*Go deeper: normalization vs. denormalization; One Big Table (OBT) vs. star schema.*
