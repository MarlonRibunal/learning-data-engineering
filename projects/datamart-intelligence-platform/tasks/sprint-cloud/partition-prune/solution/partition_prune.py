def pruned(partitions, start, end):
    return sorted(p for p in partitions if start <= p <= end)
