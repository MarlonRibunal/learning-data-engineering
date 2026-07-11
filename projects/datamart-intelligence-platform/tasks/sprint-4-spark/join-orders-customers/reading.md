## How Spark joins at scale

A join is a wide transformation, but *how* Spark executes it makes an
order-of-magnitude difference. The two strategies to know:

- **Sort-merge join** (the default for big-to-big joins) — Spark shuffles *both*
  sides so matching keys co-locate, sorts each partition, and merges. Correct for
  any size, but pays two shuffles.
- **Broadcast hash join** — when one side is small, Spark sends a full copy to
  *every* executor and joins locally, with **no shuffle** of the big side. Often
  10×+ faster. You can force it with `broadcast(small_df)`; Spark also does it
  automatically under `spark.sql.autoBroadcastJoinThreshold`.

The engineer's instinct: **broadcast the small dimension, shuffle only when both
sides are large.** Joining a billion-row fact to a small `customers` dimension?
Broadcast the customers.

The lurking danger is **data skew** — if one key holds a huge share of the rows
(a null `customer_id`, a mega-customer), its partition becomes a straggler that
one machine grinds on while the rest idle. Recognizing and mitigating skew
(salting, filtering nulls) is core Spark-tuning craft.

*Go deeper: broadcast vs. sort-merge joins; `broadcast()`; data skew & salting.*
