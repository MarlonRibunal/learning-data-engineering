## Watermarks: taming late data

Max-per-window looks like just another aggregate, but it's a good place to face the
question every streaming aggregation must answer: **when is a window done?**

On a stream, "9:00–9:10" never truly ends — a straggler event stamped 9:09 could
arrive at 9:30. So the engine can't emit a final answer or free the window's state
until it decides *no more events for this window are coming*. That decision is the
**watermark**: a moving threshold that says "I've probably seen everything up to
time T." You set how long to wait with `withWatermark("ts", "10 minutes")`.

The watermark resolves three tensions at once:

- **Completeness vs. latency** — wait longer and catch more late data, but emit
  results later. The watermark *is* that knob.
- **Late data** — events *older* than the watermark are dropped (or sent to a
  side-output), because their window is already closed.
- **Bounded state** — once the watermark passes a window, its per-key state is
  discarded, which is the *only* thing keeping streaming memory finite.

No watermark, no way to finalize windows or bound state. It's the mechanism that
makes stateful streaming actually runnable forever.

*Go deeper: watermarks; allowed lateness; the completeness/latency trade-off.*
