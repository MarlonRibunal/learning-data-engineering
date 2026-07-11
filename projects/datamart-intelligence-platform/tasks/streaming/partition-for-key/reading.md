## Partitions, keys, and the ordering guarantee

Partitions are how a topic scales — split it into N logs and N consumers read in
parallel. But parallelism and ordering are in tension, and the **key** is how
Kafka resolves it.

The guarantee, stated precisely: **order is preserved only *within* a partition,
not across the topic.** So if all of a customer's events must be processed in
order, they must land on the *same* partition — and the producer arranges that by
hashing the message key: `partition = hash(key) % num_partitions`. Same key →
same partition → ordered.

The consequences you have to design around:

- **Choosing the key is choosing your ordering boundary.** Key by `customer_id`
  and you get per-customer order; key by nothing (round-robin) and you get max
  parallelism but no order at all.
- **Partition count is a scaling ceiling** — at most one consumer per partition
  per group, so it caps your parallelism, and changing it later reshuffles the
  key→partition mapping.
- **Key skew = partition skew.** A hot key (one mega-customer) overloads its
  partition — the streaming twin of Spark's join skew.

Keying is where you trade global ordering for scale, one key at a time.

*Go deeper: partitions & the ordering guarantee; partitioning strategy; key/
partition skew.*
