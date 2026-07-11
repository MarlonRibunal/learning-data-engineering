## Lag, throughput, and backpressure

Consumer lag — produced-minus-consumed offset — is *the* health metric of a
streaming system, because it's the earliest, clearest sign of the fundamental
streaming problem: **are you keeping up?**

What lag tells you:

- **Rising lag = you're falling behind.** Consumers can't process as fast as
  producers publish. Left unchecked, lag grows until the broker's retention window
  is exceeded and you **lose data** (or blow up storage). Flat or zero lag = caught
  up.
- **Lag is your scaling signal.** The fix for sustained lag is usually more
  consumers (up to the partition count) or faster per-message processing. Lag-based
  autoscaling is a standard pattern.

The deeper concept is **backpressure**: a system's ability to signal "slow down,
I'm overwhelmed" rather than silently dropping data or running out of memory.
Kafka's design provides it *structurally* — the durable log buffers the backlog, so
a slow consumer just accumulates lag instead of crashing, and can catch up later.
Systems *without* a buffering log must implement explicit backpressure or fall over
under a spike.

Watching lag is watching the balance between ingestion rate and processing
capacity — the vital sign of any real-time pipeline.

*Go deeper: consumer lag monitoring; backpressure; throughput vs. latency.*
