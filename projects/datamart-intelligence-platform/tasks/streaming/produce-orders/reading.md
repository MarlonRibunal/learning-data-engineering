## The log: streaming's core abstraction

Under Kafka, Redpanda, Kinesis, and Pulsar sits one deceptively simple idea: the
**append-only log.** A topic is an ordered, immutable sequence of records that
producers append to and consumers read from. That's it — and it changed data
architecture.

Why the log is powerful:

- **Decoupling (pub/sub).** Producers don't know who consumes; consumers don't know
  who produced. One order-event stream can feed the warehouse, a fraud model, and a
  live dashboard — each independently, none blocking the others. Add a new consumer
  without touching the producer.
- **Replayable.** Because the log is *retained and immutable*, a new or recovered
  consumer can re-read from any point (an offset). This is what enables replay,
  backfills, and Kappa architecture's "reprocess history through the same code."
- **A shock absorber.** The broker buffers between fast producers and slow
  consumers, smoothing spikes so a traffic burst doesn't topple downstream.

Producing an event is publishing an immutable fact to a durable log that anyone can
subscribe to, now or later. That log-as-source-of-truth is the mental shift behind
event-driven data platforms.

*Go deeper: the log abstraction (Kreps, "The Log"); pub/sub; event-driven
architecture.*
