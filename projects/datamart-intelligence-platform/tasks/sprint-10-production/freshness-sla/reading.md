## Data observability and freshness

A freshness check — is this table too old? — is the entry point to **data
observability**: monitoring the *health of the data itself*, not just whether the
jobs ran. A pipeline can go green while the data silently goes wrong, and freshness
is the first and most important thing to watch.

The discipline names **five pillars** of data health to monitor:

- **Freshness** — is the data recent? (this task)
- **Volume** — did roughly the expected number of rows arrive? (a load that
  produces 0 rows "succeeded" but broke something.)
- **Schema** — did columns/types change unexpectedly?
- **Distribution** — are values in their normal range? (null rate, min/max, cardinality.)
- **Lineage** — what's upstream/downstream, so you can trace and assess impact?

The core insight is the gap between **"the job succeeded"** and **"the data is
good."** Traditional monitoring watches the former; data observability watches the
latter. A freshness SLA turns "someone will notice the dashboard is stale
eventually" into "we get paged the moment it breaches" — moving detection from your
*stakeholders* to your *monitors*. Tools like Monte Carlo, Great Expectations, and
dbt tests operationalize these pillars.

*Go deeper: data observability; the five pillars; freshness/volume/schema
monitoring.*
