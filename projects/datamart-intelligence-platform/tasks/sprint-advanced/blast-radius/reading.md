## Graphs are everywhere in data

Blast-radius is a graph traversal, and once you see it, you notice that **data
engineering is graphs all the way down.** The dependency graph you traversed here
is the same structure as:

- **Data lineage** — which tables/columns derive from which (dbt's model DAG).
  Walk it *downstream* for impact analysis ("if I change this source, what breaks?");
  walk it *upstream* for root-cause ("why is this dashboard wrong?").
- **Task DAGs** — the pipeline itself (Airflow/dbt), where topological order (the
  next Advanced level) decides run sequence.
- **Foreign-key graphs** — how entities reference each other.

BFS and DFS — the two ways to explore a graph — are the fundamental algorithms, and
the details you handled are the ones that bite in practice:

- **The `seen` set** prevents infinite loops on cycles and avoids re-visiting. Real
  lineage graphs *can* have cycles (a mistake, but they happen), so cycle-safety
  isn't optional.
- **Direction matters.** Downstream vs. upstream traversal answers opposite
  questions from the same graph.

Impact analysis — "what's the blast radius of this change/failure?" — is a question
data engineers answer constantly, and it's exactly a reachability query over the
lineage graph. Column-level lineage tools (dbt, OpenLineage, Marquez) automate it,
but the algorithm under them is the BFS you just wrote.

*Go deeper: data lineage; BFS/DFS; impact analysis; OpenLineage.*
