## Topological sort: the scheduler's heartbeat

Topological sort is the algorithm you've been *using* this whole course without
implementing it — until now. Every time dbt decides model build order, or Airflow
decides task run order, it's running a topological sort of a **DAG**.

The essentials:

- **It only works on a DAG.** "Acyclic" is load-bearing: a cycle means "A depends on
  B depends on A," which has *no* valid order — the algorithm detecting that (nodes
  left with non-zero in-degree) is exactly how orchestrators catch circular
  dependencies and refuse to run.
- **Kahn's algorithm** — repeatedly emit a node with no remaining dependencies
  (in-degree 0), remove its edges, repeat — is the intuitive formulation. DFS-based
  topo sort is the other classic.
- **Order isn't unique** — many valid orderings usually exist. Using a heap for an
  alphabetical tiebreak makes *your* output deterministic, which matters for
  reproducibility (and for grading).
- **It enables parallelism.** Nodes that become ready *simultaneously* have no
  dependency between them, so a scheduler can run them concurrently — topo sort
  finds not just an order but the whole parallel structure.

Implementing it demystifies the tools: an orchestrator is, at its core, a
topological sort plus retries, scheduling, and monitoring around it.

*Go deeper: DAGs & topological sort; Kahn's algorithm; cycle detection; critical
path.*
