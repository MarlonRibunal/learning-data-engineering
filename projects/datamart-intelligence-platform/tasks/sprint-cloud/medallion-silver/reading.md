## The lakehouse and the medallion

The medallion architecture is really a story about the **lakehouse** — the
convergence of two worlds that used to be separate:

- **Data lakes** — cheap, scalable object storage (S3/GCS) holding raw files.
  Flexible and cheap, but no transactions, no schema enforcement, easy to turn
  into a "data swamp."
- **Data warehouses** — managed, transactional, fast SQL. Reliable, but pricier
  and less flexible for raw/semi-structured data.

The **lakehouse** (Databricks' term) puts a metadata + transaction layer (Delta
Lake, Iceberg, Hudi) *over* lake storage, so you get warehouse guarantees on lake
economics. The **medallion** (bronze → silver → gold) is how you organize
refinement inside it, and it maps cleanly onto ideas you already know:

- **Bronze** = the raw/landing layer (Ingestion sprint).
- **Silver** = cleaned, deduped, conformed — dbt's *staging*, the Data Quality
  and Ingestion cleaning steps.
- **Gold** = business marts and aggregates — dbt's *marts*, the Serving sprint.

So "medallion" isn't a new technique — it's the *raw → staging → marts* pipeline
you've built all course, named for the lakehouse and applied on cheap storage.
The value is the discipline: each layer has a clear contract, and no one queries
bronze directly.

*Go deeper: the lakehouse (Databricks); medallion architecture; data lake vs.
warehouse.*
