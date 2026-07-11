# Which partition does a key go to?

**The scenario.** A Kafka/Redpanda topic is split into **partitions** — that's
how a stream scales, since consumers read partitions in parallel. But
parallelism has a catch: **ordering is only guaranteed *within* a partition**.
So if you need all of a customer's events processed in order, they must all land
on the **same partition**. The producer decides that by hashing the message
**key**.

## The partitioner

The rule every Kafka producer follows: `partition = hash(key) % num_partitions`.
The same key always hashes to the same number, so it always lands on the same
partition — that's what preserves per-key order. (Real Kafka uses a murmur2 hash
of the key's bytes; here the key is already an integer, so `key % num_partitions`
is the same idea, minus the hashing step.)

Use the **customer_id** as the key and every order for that customer stays
together and in order.

## Your task

Write `partition_for(key, num_partitions)` returning the partition index for a
key:

```python
def partition_for(key, num_partitions):
    return key % num_partitions
```

`partition_for(105, 4)` → `1`. The key point isn't the arithmetic — it's that
this function is **deterministic**: the same key always returns the same
partition, which is what keeps a customer's events ordered.
