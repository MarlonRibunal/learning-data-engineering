# Dedupe replayed offsets

**The scenario.** After a consumer restart or a rebalance, a stream can **replay**
messages you've already seen — "at-least-once" delivery means duplicates are
normal. To process each message exactly once, you dedupe by its offset (a unique,
increasing id per partition).

## The task

Return each offset once, in order — a set removes duplicates, `sorted` restores
order:

```python
def dedupe_offsets(offsets):
    return sorted(set(offsets))
```

`dedupe_offsets([3, 1, 2, 1, 3])` → `[1, 2, 3]`. Because offsets are monotonic
per partition, sorting them also puts the messages back in send order.

## Your task

Write `dedupe_offsets(offsets)` returning each offset exactly once, sorted
ascending.
