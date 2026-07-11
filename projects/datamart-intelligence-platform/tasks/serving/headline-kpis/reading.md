## The serving layer and the semantic layer

Everything upstream — ingest, transform, test — exists to feed the **serving
layer**: the tables and metrics people actually consume. Serving is the last
lifecycle stage, and its job is to make the *right* numbers *easy and fast* to
get.

The hard problem here isn't SQL — it's **agreement**. If "revenue" is `SUM(amount)`
in one dashboard and `SUM(amount) WHERE status != 'cancelled'` in another, two VPs
bring two numbers to the same meeting and trust evaporates. The modern answer is a
**semantic layer**: metrics defined *once*, centrally (dbt's metrics/MetricFlow,
LookML, Cube), so every tool computes "revenue" the same way.

Two related ideas:

- **Single source of truth** — one canonical definition per metric, referenced
  everywhere, never re-derived per dashboard.
- **Metric governance** — a KPI has an owner, a definition, and a test, just like
  a model has an owner and a schema.

So a "headline KPI" query is really the tip of an organizational agreement about
what the business measures — encoded as code so it stays consistent.

*Go deeper: semantic layers (dbt Semantic Layer, Cube, LookML); metric stores.*
