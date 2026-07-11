# Dependency blast radius

**The scenario.** A model in your DAG fails. Which dashboards, exports, and
downstream models are now stale? That "blast radius" is every node **reachable**
from the failed one by following dependency edges — a classic **graph
traversal** (BFS or DFS).

## Build the graph, then traverse

Edges are `[from, to]` — `to` depends on `from`, so if `from` breaks, `to` is
affected (and whatever depends on `to`, and so on):

```python
from collections import defaultdict, deque

def downstream(edges, failed):
    graph = defaultdict(list)
    for src, dst in edges:
        graph[src].append(dst)

    seen, queue = set(), deque([failed])
    while queue:
        node = queue.popleft()
        for nxt in graph[node]:
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return sorted(seen)
```

- Build an **adjacency list** (`from → [tos]`).
- **BFS** from the failed node, following edges, marking everything reachable.
- The `seen` set prevents infinite loops on cycles and avoids double-visiting.
- Return the affected nodes **sorted** (the failed node itself isn't in the
  output — you already know it's down).

## Your task

Write `downstream(edges, failed)` returning the sorted list of all nodes
reachable from `failed`. If `extract` fails, `transform`, `load`, and `report`
are all downstream.
