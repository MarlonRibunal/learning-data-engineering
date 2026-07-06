# The Data Engineering Lifecycle

This platform is organized around the framework from **_Fundamentals of Data
Engineering_ by Joe Reis and Matt Housley** (O'Reilly, 2022). Their central idea is
that data engineering isn't a pile of tools — it's a **lifecycle**, wrapped in a set
of **undercurrents** that run through every stage.

> This is our own summary of the framework, used to structure the curriculum — read
> the book for the full treatment. It's the best single map of the field.

## The lifecycle

```
 Generation ──▶ Ingestion ──▶ Transformation ──▶ Serving
                     │              │                │
                     └──────── Storage ─────────────┘   (underpins every stage)
```

- **Generation** — the source systems that produce data (apps, databases, APIs,
  events). On this platform: the `raw.orders` / `raw.customers` source tables.
- **Ingestion** — moving data from sources into your platform (batch or streaming,
  ETL or ELT). *(Curriculum gap today — see roadmap.)*
- **Storage** — where data lives across its life: the warehouse and its schemas
  (`raw` → `staging` → `analytics`). Postgres stands in for the warehouse here.
- **Transformation** — turning raw data into modeled, tested, business-ready tables.
  This is the **dbt sprint**.
- **Serving** — delivering data for analytics, BI, and ML. The **Streamlit dashboard**
  and the capstone's portfolio artifact. *(Room to grow — see roadmap.)*

## The undercurrents (run through every stage)

- **Security** — least privilege, protecting data. *(Gap.)*
- **Data Management** — quality, governance, contracts, lineage. Partly covered by
  dbt tests and the grader's correctness checks.
- **DataOps** — automation, observability, incident response. Covered by the test
  suite and **CI**.
- **Data Architecture** — designing systems for the tradeoffs at hand. *(Gap.)*
- **Orchestration** — scheduling and coordinating the whole thing. This is the
  **Airflow sprint**.
- **Software Engineering** — real code, tests, version control. The grader itself,
  the scaffolds, the tests, and CI model this throughout.

## How the platform maps today

| Lifecycle stage / undercurrent | On this platform | Status |
|---|---|---|
| Generation | `raw.*` source tables (seed) | ✅ |
| Ingestion | — | ⛳ gap |
| Storage | Postgres warehouse, `raw`/`staging`/`analytics` schemas | ✅ |
| Transformation | dbt sprint (models + tests) | ✅ |
| Serving | Streamlit dashboard, capstone artifact | 🟡 light |
| Orchestration | Airflow sprint | ✅ |
| Data Management (quality) | dbt tests, grader correctness checks | 🟡 partial |
| DataOps | test suite + CI | 🟡 partial |
| Software Engineering | grader, scaffolds, tests, CI | ✅ |
| Security / Data Architecture | — | ⛳ gap |

## Roadmap to "zero to hero" (fill the lifecycle)

Ordered by how much each closes the gap between "can write SQL" and "can own a
pipeline in production":

1. **Ingestion sprint** — extract from a file/API into `raw` (the missing front of
   the lifecycle). Teaches ELT, incremental loads, idempotency.
2. **Data Quality sprint** — author dbt tests, freshness, and data contracts; catch
   bad data before it ships. The Data Management undercurrent, made concrete.
3. **Serving / BI sprint** — build the metrics + dashboard a stakeholder actually
   reads. Turns "I made a table" into "I delivered an answer."
4. **Streaming sprint** — real-time ingestion + processing with Redpanda (already on
   the backlog). The other half of ingestion.
5. **Undercurrents woven in** — security (least-privilege DB roles), architecture
   (batch vs streaming tradeoffs), DataOps (monitoring/alerting) as capstone-level
   challenges.

Each new sprint follows the same shape the platform already uses: a ladder of
scaffold → solution tasks, graded against the real stack, ending in a portfolio
artifact.
