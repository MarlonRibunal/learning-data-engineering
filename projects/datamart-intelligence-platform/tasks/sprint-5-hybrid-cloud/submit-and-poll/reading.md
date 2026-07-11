## Control plane vs. data plane

Orchestrating an external job separates two concerns that are easy to conflate:

- The **data plane** — where the heavy work actually happens (Spark crunching on
  Databricks, a query running in BigQuery). Big, expensive, remote.
- The **control plane** — the thin layer that *coordinates* it: submit the job,
  track it, react to the result. That's your Airflow task, and it moves *no data*
  — just commands and status.

Async orchestration is fundamentally about the control plane talking to a data
plane it doesn't own. That framing explains the whole submit-then-poll shape:
because the job runs *elsewhere*, submission returns immediately with a handle,
and you have no choice but to poll (or await a callback) for completion.

Two integration styles do the polling for you:

- **Polling** (this task) — ask "done yet?" on an interval. Simple, works
  anywhere, but wastes calls and adds latency.
- **Webhooks / callbacks** — the service notifies *you* on completion. Efficient,
  but needs an endpoint the service can reach.

Recognizing "I'm the control plane coordinating a remote data plane" is the mental
model behind every operator that talks to a cloud service.

*Go deeper: control plane vs. data plane; polling vs. webhooks; the operator
pattern.*
