### Orchestrate with Airflow

Data pipelines don't run themselves — an **orchestrator** schedules and runs them.
Airflow is the most common one. A pipeline is a **DAG** (a graph of tasks).

**Your task:** the `hello_grader` DAG has one task that currently *raises an
exception*, so the DAG run fails. Fix it so the task finishes normally and the
run ends in state **success**.

Open the DAG file, find `run(...)`, and make it return a value instead of raising.

When you check, the grader **unpauses and triggers the real DAG** in the Airflow
container, then polls until it finishes. Green means a real Airflow run succeeded —
exactly what you'd watch for on the job.

> Needs the stack running: `docker compose up -d` first.
