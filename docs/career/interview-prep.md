# The Data Engineering Interview

A map of what DE interviews actually test, and how the work in this repo maps to each. Study the topic, then point to the sprint where you *did* it.

## The five rounds you'll usually see

1. **SQL / data manipulation** — window functions, joins, aggregation, dedup.
   → *SQL Fundamentals, Ingestion, Serving sprints.*
2. **Data modeling** — dimensional modeling, grain, facts vs. dimensions, SCDs.
   → *Architecture sprint (dim/fact), dbt sprint.*
3. **Pipeline / systems design** — "design a pipeline for X" (see `system-design.md`).
   → *Airflow, Hybrid Cloud, Streaming sprints.*
4. **Coding** — Python data wrangling, sometimes Spark.
   → *Spark, Real-time, Dashboard, Production sprints.*
5. **Behavioral** — ownership, incidents, trade-offs, working with stakeholders.

## Questions you should be able to answer cold

- **Idempotency:** "Your job reran and double-counted. Why, and how do you fix it?"
  → last-write-wins upsert / dedup by key (you built this in *Production*).
- **Late & out-of-order data:** "How do windowed aggregates handle stragglers?"
  → watermarks bound state and drop data past the allowed lateness (*Real-time*).
- **Batch vs. streaming:** when each is appropriate; how windowing unifies them.
- **Backfills:** how to reprocess history without corrupting current data.
- **Data quality:** how you'd catch a bad upstream change before it reaches BI
  → clean-vs-dirty tests (*Data Quality*).
- **Star schema:** grain, conformed dimensions, why you don't join facts to facts.
- **Orchestration:** retries, backoff, SLAs, alerting on failure vs. on staleness.

## How to prep with this repo

For each sprint you passed, be able to say in 60 seconds: **what problem it
solves, what you built, and one trade-off you made.** That's a portfolio story
and a behavioral answer at once. The graded proof artifacts (`portfolio/`) are
your receipts.
