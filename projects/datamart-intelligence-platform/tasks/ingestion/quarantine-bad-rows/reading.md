## The dead-letter pattern

When a bad record arrives, you have three options, and only one is
production-grade. Let it through → it poisons downstream reports. Fail the whole
batch → one bad row blocks thousands of good ones. **Quarantine it** → load the
good, set the bad aside for investigation, keep moving.

That set-aside is a **dead-letter queue / table** (the name comes from
messaging systems, where undeliverable messages go to a "dead-letter" queue). The
principles that make it work:

- **Never silently drop.** A rejected row must land *somewhere*, with enough
  context (and a reason) to fix it. Data that vanishes is worse than data that's
  wrong, because no one knows to look.
- **Make it observable.** A quarantine table that grows is an alert: something
  upstream changed. Monitoring its size is a cheap, powerful data-quality signal.
- **Make it reprocessable.** Once the root cause is fixed, you replay the
  quarantined rows back through the pipeline.

Resilient ingestion isn't ingestion that never sees bad data — it's ingestion
that has a *designated place* for bad data and keeps the good flowing.

*Go deeper: dead-letter queues; error-handling patterns in data pipelines.*
