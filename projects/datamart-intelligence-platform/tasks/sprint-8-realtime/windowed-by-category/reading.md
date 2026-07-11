## Keyed streams and per-key state

Grouping by `window` **and** `category` turns one stream into many independent
sub-streams — a **keyed stream** — and that keying is the backbone of scalable
streaming.

Why keying is fundamental:

- **Parallelism.** Each key's events can be processed independently, so the engine
  distributes keys across machines. More keys → more parallelism. (Kafka
  partitioning by key, from the Streaming sprint, is the same idea feeding this.)
- **State is per key.** A streaming aggregate isn't computed from scratch each time
  — it maintains a *running* value **per (window, key)** in a state store, updated
  as events arrive. Group by window+category and you're keeping a separate running
  total for every category in every window.

That per-key state is what makes streaming aggregation possible on an unbounded
input — and also what makes it *dangerous*: state grows with the number of active
keys. A high-cardinality key (user_id × window) can blow up memory. Which is
exactly why watermarks (to expire old windows' state) and bounded-state tricks
matter, and why they're the subject of the levels around this one.

*Go deeper: keyed streams; per-key state stores; state and key cardinality.*
