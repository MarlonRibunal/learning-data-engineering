## Parallelism and executors

Fanning out — one task kicking off several that run at once — only *actually*
runs in parallel if the thing executing your tasks can do more than one at a time.
That thing is the **executor**, and which one you use decides your pipeline's
scale.

- **SequentialExecutor** — one task at a time. The default with a SQLite
  metadata DB; fine for a demo, useless for real work (your fan-out would run
  one-by-one).
- **LocalExecutor** — runs tasks as parallel processes on a single machine. Great
  for moderate workloads; parallelism is capped by that box's cores.
- **CeleryExecutor** — distributes tasks to a fleet of worker machines via a
  queue. Horizontal scale for large, always-on deployments.
- **KubernetesExecutor** — launches each task in its own pod, so every task gets
  isolated, right-sized resources and scales elastically.

Two dials bound how much actually runs concurrently: **`parallelism`** (cluster-
wide task slots) and **`max_active_tasks`** per DAG. Fan-out beyond those just
queues.

The lesson: the *graph* expresses what *could* be parallel (independent tasks),
but the *executor and its limits* decide what *is*. Designing wide, independent
task graphs is only half the speed-up — the runtime has to be able to cash it in.

*Go deeper: Airflow "Executors"; the `parallelism` / `max_active_tasks` settings.*
