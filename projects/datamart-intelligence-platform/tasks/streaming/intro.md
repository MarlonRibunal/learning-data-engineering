**Not all data arrives in nightly batches.** Streaming processes each event the moment
it happens — orders, clicks, sensor readings — with low latency. **Redpanda** (a
Kafka-compatible broker) moves those events. Here you write the two halves of every
streaming pipeline: a **producer** that publishes events, and a **consumer** that reads
them.
