## Co-partitioning and stateful streams

Routing a batch of events by key is the same partitioner applied at scale — and
its real importance shows up once your stream processing becomes **stateful**.

Consider a streaming join or a per-key aggregation (revenue per customer). For a
worker to maintain a customer's running state locally, *every* event for that
customer must reach *that* worker. Consistent key-based routing guarantees it. And
when two streams are joined, they must be **co-partitioned** — partitioned by the
same key into the same number of partitions — so matching keys meet on the same
node without a reshuffle.

This is why keying is foundational to streaming, not a detail:

- **State locality.** Per-key state lives with the partition, so all of a key's
  events must route together, consistently, forever (even across restarts).
- **Co-partitioning enables local joins/aggregations** — no cross-network shuffle
  per event, which would be ruinous at stream volumes.
- **Repartitioning is expensive and rare**, so you choose the key up front to match
  how you'll process (join/aggregate) downstream.

Routing isn't just load-balancing; it's arranging the data so stateful, ordered,
per-key computation is even *possible* on an infinite stream.

*Go deeper: co-partitioning; stateful stream processing; local state stores.*
