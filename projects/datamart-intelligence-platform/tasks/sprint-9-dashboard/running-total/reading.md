## Cumulative views and pacing

A running (cumulative) total answers a different question than a daily bar: not
"how much *each* day" but "how much **so far**" — and it's the natural shape for
**goal tracking**. Overlay a cumulative-revenue line against a target line and you
instantly see *pacing*: are we ahead of or behind plan, right now?

Why cumulative charts are so effective for decisions:

- **They show trajectory, not just position.** A slope tells you the *rate* — a
  flattening cumulative line signals momentum dying before any single day looks
  alarming.
- **They pair with a target/"burn-up".** Cumulative-actual vs. cumulative-goal is
  the canonical "will we hit the number?" view (the same burn-up chart used in
  sprint planning).
- **They're monotonic** for non-negative measures — always rising — which makes
  "falling behind" read as "rising too slowly," a subtle but important framing.

Engineering-wise, the running total connects to the serving sprint's
precompute-vs-read choice: cheap to compute with a window on small data, worth
materializing on large. And ordering is everything — a cumulative sum is
meaningless unless the rows are in true time order.

*Go deeper: cumulative/burn-up charts; pacing vs. targets; monotonic series.*
