# Route a batch of events by key

**The scenario.** You're producing a batch of order events to a 4-partition
topic. To preserve per-customer ordering, each event must be routed to a
partition **by its customer key** — using the same partitioner from the last
level. Do it consistently and every event for customer 10 lands on the same
partition, in order; get it wrong and a customer's timeline gets shuffled across
partitions and processed out of order.

Notice in the expected output that customers 10 and 14 both route to partition
**2** (`10 % 4 == 14 % 4 == 2`). That's fine and expected — a partition happily
holds *multiple* keys. What matters is that a *single* key never splits across
partitions.

## Your task

Write `assign_partitions(events, num_partitions)` returning a list of the
partition index for each event, keyed by `customer_id`:

```python
def assign_partitions(events, num_partitions):
    return [event["customer_id"] % num_partitions for event in events]
```

For 3 events with customer_ids 10, 11, 14 over 4 partitions →
`[2, 3, 2]`. Same partitioner as before, applied across the batch.
