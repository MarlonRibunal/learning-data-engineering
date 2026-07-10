**Hybrid cloud: orchestrating external jobs.** Real pipelines rarely live in one system. A common shape: your orchestrator (Airflow, running locally) kicks off a heavy job on an external service (a Spark job on Databricks, a query on BigQuery), then waits for it to finish before moving on.

That "fire a job, then wait for it" dance has a precise shape, and getting it right is what separates a robust pipeline from a flaky one:

1. **Submit** the job → get back a run handle.
2. **Poll** its status until the run reaches a terminal state.
3. **Succeed** → return the result and continue downstream.
4. **Fail** → raise, so the pipeline stops instead of marching on with missing data.

This is exactly what an Airflow `DatabricksOperator` does under the hood. Here you'll implement it against a **local mock client** — no cloud account, no network, fully deterministic — so you learn the pattern, not the vendor SDK.

The grader hands your function a `client` with `submit(job_id)`, `get_status(run_id)`, and `get_result(run_id)`.
