## Consumption pricing and FinOps

The pay-per-byte model isn't a billing quirk — it's the defining shift of the
cloud data era, and it changes the data engineer's job. On-prem, compute was a
fixed cost you'd already paid; on a serverless cloud warehouse, **every query has
a price tag**, and inefficiency shows up on an invoice.

This gave rise to **FinOps** (cloud financial operations) — treating cost as a
first-class engineering metric alongside latency and correctness:

- **Two pricing models.** *On-demand* (BigQuery) bills by bytes scanned — great
  for spiky, unpredictable workloads. *Capacity/flat-rate* (reserved slots,
  Snowflake warehouses) bills for provisioned compute-time — cheaper at steady
  high volume. Choosing between them is a real architecture decision.
- **The knobs an engineer controls:** scan less (column pruning, partition
  pruning, clustering), materialize expensive repeated queries, and set **cost
  guardrails** (per-query byte limits, budget alerts) so a runaway `SELECT *` on a
  dashboard can't quietly cost thousands.

The mindset: on the cloud, a query's *cost* is as much your responsibility as its
*result*. "It returns the right answer" is table stakes; "it returns it without
scanning 10 TB" is the craft.

*Go deeper: BigQuery on-demand vs. capacity pricing; FinOps; cost guardrails.*
