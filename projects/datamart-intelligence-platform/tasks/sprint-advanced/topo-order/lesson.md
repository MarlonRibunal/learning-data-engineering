# Topological order of a DAG

**The scenario.** An orchestrator (Airflow, Dagster) is handed a DAG of tasks
with dependencies and must decide a run order where **every task runs after the
tasks it depends on**. That's a **topological sort** — the scheduling algorithm
at the heart of every pipeline tool. You'll implement the classic **Kahn's
algorithm**.

## Kahn's algorithm

Repeatedly take a node with no remaining dependencies, output it, and remove its
edges — which may free up new nodes:

```python
from collections import defaultdict
import heapq

def topo_order(edges):
    graph, indeg, nodes = defaultdict(list), defaultdict(int), set()
    for src, dst in edges:
        graph[src].append(dst)
        indeg[dst] += 1
        nodes |= {src, dst}

    ready = [n for n in nodes if indeg[n] == 0]
    heapq.heapify(ready)              # a heap breaks ties deterministically
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for nxt in sorted(graph[node]):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                heapq.heappush(ready, nxt)
    return order
```

- **`indeg`** = how many dependencies each node still has; a node is `ready` when
  it hits `0`.
- Using a **heap** (min-heap) instead of a plain list makes the output
  deterministic: among equally-ready nodes, the alphabetically smallest goes
  first. (Without it, many valid orders exist.)

## Your task

Write `topo_order(edges)` returning a valid run order (alphabetical tiebreak).
For `a→b`, `a→c`, `b→d`, `c→d` the order is `[a, b, c, d]`.
