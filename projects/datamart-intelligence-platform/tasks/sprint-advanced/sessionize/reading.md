## Stateful passes and the shape of sessionization

Counting sessions with a single stateful pass is a small instance of a big pattern:
**a linear scan that carries state**, deciding each step from what came before. It's
the CPU-level cousin of the streaming session windows you built — same logic, minus
the distribution.

Why this shape recurs:

- **Gap-and-islands.** "Group consecutive things separated by gaps" is a named SQL
  problem (gaps-and-islands) that shows up everywhere: user sessions, consecutive
  login streaks, contiguous date ranges, price periods. Recognizing a task *as*
  gaps-and-islands instantly suggests the technique (compare each row to the
  previous; a jump starts a new island).
- **Order is a precondition.** Sessions only mean anything in time order — sort
  first, always. On a stream, that's why event-time and watermarks matter; in a
  batch, it's a `sort`.
- **O(n), one pass.** Carrying a tiny bit of state (the previous timestamp) lets you
  solve in a single linear pass what a naive approach might do with an expensive
  self-join.

Sessionization is where "raw events" become "human behavior," and the
compare-to-previous, carry-state technique is a workhorse you'll reuse for streaks,
run-length encoding, and change detection.

*Go deeper: gaps-and-islands; run-length encoding; stateful single-pass algorithms;
`LAG` in SQL.*
