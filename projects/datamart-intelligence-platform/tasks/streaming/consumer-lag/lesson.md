# How far behind is the consumer?

**The scenario.** In streaming, the number-one health metric is **consumer lag**:
how many messages have been produced that your consumer hasn't processed yet. Lag
that grows means you're falling behind real time — the single most important
number on a streaming dashboard.

## The task

Lag is the gap between the latest offset on the partition and the last offset the
consumer committed:

```python
def consumer_lag(latest_offset, committed_offset):
    return latest_offset - committed_offset
```

`consumer_lag(1000, 950)` → `50` — fifty messages produced but not yet processed.
Zero means fully caught up; a steadily rising number means scale up your
consumers.

## Your task

Write `consumer_lag(latest_offset, committed_offset)` returning the number of
un-processed messages.
