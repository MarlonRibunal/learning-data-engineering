## A taxonomy of windows

"Window" isn't one thing — streaming defines a family, each answering a different
question, and knowing which to reach for is core streaming literacy.

- **Tumbling** — fixed, non-overlapping (revenue *each* 10 minutes). Every event
  in exactly one window. The default.
- **Sliding** (this task) — fixed width, advancing by a smaller step, so windows
  **overlap** ("last 10 minutes, updated every 5"). Smoother, more responsive —
  but each event now lands in *multiple* windows, so it costs more state and
  compute.
- **Session** — no fixed size; bounded by inactivity gaps (next level). Windows
  grow to fit a burst of activity.
- **Global** — one unbounded window; you supply your own trigger to emit.

The trade-off sliding windows make is worth internalizing: **overlap buys
freshness at the cost of work.** A 10-min/1-min sliding window updates ten times as
often as tumbling and holds each event in ten windows. Responsiveness isn't free —
it's paid in state and CPU.

Picking the window is picking how you trade latency, smoothness, and cost for the
metric at hand.

*Go deeper: tumbling/sliding/session/global windows; state cost of overlap.*
