**Not all data arrives in nightly batches.** Streaming processes each event the moment
it happens — orders, clicks, sensor readings — with low latency. **Redpanda** (a
Kafka-compatible broker) moves those events. Here you write the two halves of every
streaming pipeline: a **producer** that publishes events, and a **consumer** that reads
them.

**Watch it flow:** open the **Redpanda Console** at [localhost:8082](http://localhost:8082)
— also linked from the **Platform** page — to see your events land on the topic in real
time as your producer runs, and inspect message keys, partitions, and offsets.
