## Offsets and consumer groups

Consuming from a log is more than "read the messages" — it's a small distributed
system built on two ideas: **offsets** and **consumer groups.**

- **Offsets** are each consumer's bookmark. The broker doesn't track "who read
  what"; the consumer records the offset it has processed up to. **Committing** an
  offset says "I'm done through here." This is why a consumer can crash and resume
  where it left off — and why *when* you commit determines your delivery
  guarantee (commit before processing → at-most-once; after → at-least-once).

- **Consumer groups** are how you scale reads. A topic's partitions are divided
  among the consumers in a group — each partition read by exactly one member — so
  adding consumers (up to the partition count) adds throughput. When a member joins
  or dies, the group **rebalances**, reassigning partitions.

Two independent groups reading the same topic each get *every* message (broadcast);
members *within* a group split the work (load balancing). That single mechanism
gives you both fan-out to many systems and scale-out within one.

Consuming well is really about managing offsets and group membership so processing
is scalable *and* recoverable.

*Go deeper: offsets & commit strategies; consumer groups & rebalancing.*
