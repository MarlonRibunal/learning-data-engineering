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
