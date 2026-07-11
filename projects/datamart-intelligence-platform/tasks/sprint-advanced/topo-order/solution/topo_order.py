from collections import defaultdict
import heapq


def topo_order(edges):
    graph, indeg, nodes = defaultdict(list), defaultdict(int), set()
    for src, dst in edges:
        graph[src].append(dst)
        indeg[dst] += 1
        nodes |= {src, dst}

    ready = [n for n in nodes if indeg[n] == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for nxt in sorted(graph[node]):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                heapq.heappush(ready, nxt)
    return order
