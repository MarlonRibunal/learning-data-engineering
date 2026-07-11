## Dependencies, idempotency, and the graph

Setting `extract >> load` does two things: it makes `load` wait for `extract`,
and it tells Airflow these tasks form an **edge** in the DAG. From all those
edges Airflow knows the whole execution order — and which tasks can run *at the
same time* (anything with no dependency between them).

Two ideas make task dependencies actually reliable:

- **Tasks should be idempotent.** A task can be retried, or a day re-run during a
  backfill — so running it twice must produce the same result as running it once.
  "Insert today's rows" is dangerous (double-loads on retry); "replace today's
  partition" is safe. Idempotency is *the* golden rule of pipeline tasks, and it's
  why the Ingestion and Production sprints drilled upserts and dedup so hard.

- **Tasks should be atomic.** One task should do one thing. If extract-and-load
  are a single task and load fails, you can't re-run just the load. Splitting them
  (with a dependency) means a failure only re-runs what's broken.

So the humble `>>` is really you designing for **recovery**: a graph of small,
idempotent, atomic steps that Airflow can re-run piece by piece when something
goes wrong at 3am.

*Go deeper: Airflow "Task Dependencies"; idempotency & atomicity in pipelines.*
