## What an orchestrator does

A pipeline is a set of tasks — extract, transform, load, test. Something has to
decide *when* each runs, *in what order*, *what happens on failure*, and *whether
last night's run even succeeded*. That something is an **orchestrator**, and
Airflow is the most widely used one.

Airflow's core abstraction is the **DAG** — a Directed Acyclic Graph of tasks.
"Directed" (edges point from a task to its dependents), "acyclic" (no loops, or a
task could wait on itself forever). You *define the graph in Python*; Airflow
*runs it*.

The pieces:

- **DAG** — the pipeline definition (its tasks and their dependencies).
- **Task / Operator** — one unit of work. An *operator* is a template
  (`PythonOperator` runs a function, `BashOperator` a command, `DatabricksOperator`
  a cloud job); a *task* is an operator instance in a DAG.
- **Scheduler** — the always-on process that decides which tasks are ready and
  queues them.
- **Executor** — how queued tasks actually run (locally, or across a cluster).
- **Web UI** — where you watch runs, read logs, and re-trigger failures.

So writing a DAG isn't writing the work itself — it's declaring the *shape* of the
pipeline so a robust system can run, monitor, and recover it for you.

*Go deeper: Airflow "Core Concepts" — DAGs, operators, scheduler, executor.*
